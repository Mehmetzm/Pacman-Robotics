#!/usr/bin/env python3
import rclpy, math, cv2, random, numpy as np
from rclpy.node import Node
from picamera2 import Picamera2
from geometry_msgs.msg import Twist
from tf2_msgs.msg import TFMessage
from std_msgs.msg import String

light_treshold = 195 #195 # 200 ohne Licht | 180 bei licht
dark_treshold = 200
boost_speed = 0.2 #experimentiell
normal_speed = 0.1 #experimentiell

class PathfinderStream(Node):
    def __init__(self):
        super().__init__('pacman_controll')
        #subs und pubs
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscription = self.create_subscription(TFMessage, '/tf', self.tf_callback, 1)
        self.logik_sub = self.create_subscription(String,'/logik', self.logik_callback, 1)
        self.controll_sub = self.create_subscription(String,'/controll', self.controll_callback, 1)

        #params
        self.linear_speed = 0.1
        self.kp = 0.0005
        self.kj = 0.005
        self.kreuzung_rechts = False
        self.kreuzung_links = False
        self.State = "fahren"
        self.timer = None
        self.error_queue = []
        self.debug_counter = 0
        self.erkennung = True
        self.threshold = 160
        self.next_move = ""
        self.controll = ""
        self.current_yaw = 0.0
        self.ziel_yaw = 0.0

        self.timer = self.create_timer(0.05, self.capture_and_calculate)

        # Kamera Setup
        self.video_w, self.video_h = 1920, 1080
        self.lo_w, self.lo_h = 1920, 1080
        self.picam2_0 = Picamera2(camera_num=0)
        self.picam2_1 = Picamera2(camera_num=1)

        main_config = {'size': (self.video_w, self.video_h), 'format': 'XRGB8888'}
        lores_config = {'size': (self.lo_w, self.lo_h), 'format': 'YUV420'}
        controls = {'FrameRate': 20}

        config_0 = self.picam2_0.create_video_configuration(main_config, lores=lores_config, buffer_count=2, controls=controls)
        config_1 = self.picam2_1.create_video_configuration(main_config, lores=lores_config, buffer_count=2, controls=controls)

        self.picam2_0.configure(config_0)
        self.picam2_1.configure(config_1)
        self.picam2_0.start()
        self.picam2_1.start()

    # Callback für die Wegfindungsentscheidung
    def logik_callback(self, msg):
        if msg.data in ["links", "rechts", "geradeaus", "umkehren"]:
            if self.next_move != msg.data:
                self.get_logger().info(f"nächste Bewegung erhalten:{msg.data}")
                self.next_move = msg.data    
        else:
            self.next_move = ""

    # Callback für die Controllersteuerung
    def controll_callback(self, msg):
        if msg in ["links", "rechts", "geradeaus", "umkehren"]:
            self.controll = msg
        elif msg.data == "boost":
            self.linear_speed = boost_speed
        elif msg.data != "boost":
            self.linear_speed = normal_speed
        else:
            self.controll = ""

    # Umrechnung Quaternion zu Yaw, ACHTUNG: ohne die emaros_status_information node funktioniert die Steuerung nicht
    def tf_callback(self, msg):
        for transform in msg.transforms:
            if transform.child_frame_id == 'emaros_base_link' and transform.header.frame_id == 'odom':
                q = transform.transform.rotation
                siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)       
                cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z) 
                yaw = math.atan2(siny_cosp, cosy_cosp)         
                yaw_deg = math.degrees(yaw)                     
                yaw_deg = (yaw_deg + 360) % 360                 
                self.current_yaw = yaw_deg                      

    def capture_and_calculate(self):
        frame_0 = self.picam2_0.capture_array('main')
        frame_1 = self.picam2_1.capture_array('main')

        height = 200
        width = 1344

        x_start_0, x_end_0 = 0, width
        x_start_1, x_end_1 = self.video_w - width, self.video_w

        cropped_alt_0 = frame_0[:, x_start_0+200:x_end_0]
        cropped_alt_1 = frame_1[:, x_start_1:x_end_1-200]

        stitched = np.hstack((cropped_alt_0, cropped_alt_1))        #alternativer Schnitt  (0.2sek) CPU Usage ~ 20%; 40% RAM Usage

        ##################################### zum publishen des Bildes ########################################
        # einkommentieren, wenn das Bild von einer anderen Node gebraucht wird

        # encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        # success, encoded_image = cv2.imencode('.jpg', stitched, encode_param)

        # if success:
        #     msg = CompressedImage()
        #     msg.header.stamp = self.get_clock().now().to_msg()
        #     msg.format = "jpeg"
        #     msg.data = encoded_image.tobytes()
        #     self.publisher_.publish(msg)
        # else:
        #     self.get_logger().error("Image encoding failed")

        ########################################################################################################

        grey = cv2.cvtColor(stitched, cv2.COLOR_BGR2GRAY) 
        h, self.breite = grey.shape
        offset = 400 #müsste dynamisch der Bildgröße angepasst werden
        
        #Bildausschnitte, müssten je nach Anwendungsbeispiel angepasst werden
        geradeaus = grey[int(4/5 * h):, int(1/4 * self.breite) : int(3/4 * self.breite)]                           #Beschneidung um die Fahrtrichtung zu berechnen
        rechts = grey[int(8/10 * h) : int(9/10 * h), int(2/4 * self.breite + offset) : int(3/4 * self.breite) ]    #Beschneidung um den Zustand nach rechts zu bestimmen
        links = grey[int(8/10 * h) : int(9/10 * h), int(1/4 * self.breite) : int(2/4 * self.breite - offset) ]     #Beschneidung um den Zustand nach links zu bestimmen

        blur_geradeaus = cv2.GaussianBlur(geradeaus, (5, 5), 0)
        blur_rechts = cv2.GaussianBlur(rechts, (5, 5), 0)
        blur_links = cv2.GaussianBlur(links, (5, 5), 0)

        _, thresh_geradeaus = cv2.threshold(blur_geradeaus, light_treshold, 255, cv2.THRESH_BINARY) #Pixel mit >150 --> 0 ; Pixel mit <= 150 --> 255 gesetzt. THRESH_BINARY_INV | THRESH_BINARY
        _, thresh_rechts = cv2.threshold(blur_rechts, light_treshold, 255, cv2.THRESH_BINARY)
        _, thresh_links = cv2.threshold(blur_links, light_treshold, 255, cv2.THRESH_BINARY)

        self.contours_geradeaus, _ = cv2.findContours(thresh_geradeaus, 1, cv2.CHAIN_APPROX_NONE)
        for contour in self.contours_geradeaus:
            contour += [int(1/4 * self.breite), int(4/5 * h)]
        contours_rechts, _ = cv2.findContours(thresh_rechts, 1, cv2.CHAIN_APPROX_NONE)
        for contour in contours_rechts:
            contour += [int(2/4 * self.breite + offset), int(8/10 * h)]
        contours_links, _ = cv2.findContours(thresh_links, 1, cv2.CHAIN_APPROX_NONE)
        for contour in contours_links:
            contour += [int(1/4 * self.breite), int(8/10 * h)]


        ####################################################################### STATEMACHINE #############################################################################

        twist = Twist()
        if self.State == "fahren":##################################################################### STATEMACHINE: Fahren
            if self.controll == "umkehren":#manuelle Steuerung kann jederzeit umkehren, TODO man kann allerdings so in ein Errorstate kommen

                self.State = "abbiegen"
            if self.kreuzung_rechts or self.kreuzung_links:########################################### Fall: abbiegen
                self.close_gap_asynchron()
            if self.contours_geradeaus:################################################################ Fall: normales Fahren
                error = self.get_error()
                if error:
                    twist.linear.x = self.linear_speed
                    twist.angular.z = -error * self.kp
                    if abs(error) >= 300:
                        self.erkennung = False
                    else:
                        self.erkennung = True
                    if len(self.error_queue) > 5:
                        self.error_queue.pop(0)
                    self.error_queue.append(abs(error))
                    #self.get_logger().info(f"mean={np.mean(self.error_queue)}")
                    #self.get_logger().info(f"Error={error}")
            elif np.mean(self.error_queue) >= 500:#################################################### Fall: überschwenkt #TODO
                self.get_logger().info(f"überschwenkt, mean={np.mean(self.error_queue)}")
                self.State = "ausrichten"
            else: #er hat die Linie eine gewisse Zeit verfolgt, der mean error ist klein dh. er ist nicht übersteuert --> es muss eine Sackgasse sein --> State abbiegen
                self.close_gap_asynchron()
            self.cmd_pub.publish(twist)
        elif self.State == "abbiegen":##################################################################### STATEMACHINE: Abbiegen
            if self.kreuzung_rechts and self.kreuzung_links and self.contours_geradeaus:################### Fall: +-Kreuzung
                self.get_logger().info(f"Fall: +-Kreuzung, next_move={self.next_move}")
                wahl = random.choice(["links", "rechts"])#, "umkehren"]) #ausgeklammert, da zu häufig "zufällig" gewählt 
                if self.controll != "":################## Falls Manuelle Steuerung verfügbar
                    self.make_decision(self.controll)
                    self.controll = ""
                elif self.next_move != "":############### Falls Logik-Steuerung verfügbar
                    self.make_decision(self.next_move)
                    self.next_move = ""
                elif wahl in ["links", "rechts"]:######## Falls nichts verfügbar -> zufällig
                    self.get_logger().info(f"Fall: {wahl}-Abbiegung")
                    self.abbiegen_asynchron(wahl)
                elif wahl == "umkehren":
                    self.get_logger().info(f"Fall: umkehren")
                    self.turn_asynchron()
                else:
                    self.get_logger().info("geradeaus")
                    self.close_gap_asynchron()
                    self.kreuzung_rechts = False
                    self.kreuzung_links = False
                    self.State = "fahren"
            elif self.kreuzung_rechts and self.kreuzung_links:######################################## Fall: T-Kreuzung
                self.get_logger().info(f"Fall: T-Kreuzung, next_move={self.next_move}")
                wahl = random.choice(["links", "rechts"])#, "umkehren"])
                if self.controll != "":
                    self.make_decision(self.controll)
                    self.controll = ""
                elif self.next_move != "":
                    self.make_decision(self.next_move)
                    self.next_move = ""
                elif wahl in ["links", "rechts"]:
                    self.get_logger().info(f"Fall: {wahl}-Abbiegung")
                    self.abbiegen_asynchron(wahl)
                else:
                    self.get_logger().info(f"Fall: umkehren")
                    self.turn_asynchron()
            elif self.kreuzung_links:################################################################# Fall: Links Abbiegen
                self.get_logger().info(f"Fall: L-Kreuzung, next_move={self.next_move}")
                wahl = random.choice(["links"])#, "umkehren"])
                if self.controll in ["links", "umkehren"]:
                    self.make_decision(self.controll)
                    self.controll = ""
                elif self.next_move in ["links", "umkehren"]:
                    self.make_decision(self.next_move)
                    self.next_move = ""
                elif wahl == "umkehren":
                    self.get_logger().info(f"Fall: umkehren")
                    self.turn_asynchron()
                else:
                    self.abbiegen_asynchron("links")
            elif self.kreuzung_rechts:################################################################ Fall: Rechts Abbiegen
                self.get_logger().info(f"Fall: R-Kreuzung, next_move={self.next_move}")
                wahl = random.choice(["rechts"])#, "umkehren"])
                if self.controll in ["rechts", "umkehren"]:
                    self.make_decision(self.controll)
                    self.controll = ""
                elif self.next_move in ["rechts", "umkehren"]:
                    self.make_decision(self.next_move)
                    self.next_move = ""
                elif wahl == "umkehren":
                    self.get_logger().info(f"Fall: umkehren")
                    self.turn_asynchron()
                else:
                    self.abbiegen_asynchron("rechts")
            else:
                self.get_logger().info("Fall: umkehren")
                self.turn_asynchron()
        elif self.State == "ausrichten":############################################################## STATEMACHINE: ausrichten
            if self.contours_geradeaus:#################################################################### Fall: Linie wird erkannt
                self.search_line(False)
            else:##################################################################################### Fall: Linie wird nicht erkannt
                self.search_line(True)
        elif self.State == "waiting":################################################################# STATEMACHINE: waiting
            pass

        ################################ Zustandserkennung ######################################
        #################################       rechts      #####################################
        if self.erkennung:
            if contours_rechts:
                M = cv2.moments(max(contours_rechts, key=cv2.contourArea))
                if M and M['m00'] > 5500 and not self.kreuzung_rechts:
                    self.kreuzung_rechts = True
                    #self.get_logger().info(f"man kann rechts abbiegen")
        ################################        links       #####################################
            if contours_links:
                M = cv2.moments(max(contours_links, key=cv2.contourArea))
                if M and M['m00'] > 5500 and not self.kreuzung_links:
                    self.kreuzung_links = True
                    #self.get_logger().info(f"man kann links abbiegen")
        #########################################################################################

    ################################### Hilfsfunktionen #########################################
    def abbiegen_asynchron(self, richtung):
        self.State = "waiting"
        self.erkennung = False
        self.richtung = richtung
        if self.richtung  == "rechts":
            self.ziel_yaw = (self.current_yaw - 90.0) % 360
        else: 
            self.ziel_yaw = (self.current_yaw + 90.0) % 360
        #self.get_logger().info(f"Zielwinkel: {self.ziel_yaw}") #debug
        self.timer = self.create_timer(0.05, self.abbiegen_callback)
        self.timer_start = self.get_clock().now()
        self.timer_dauer = rclpy.duration.Duration(seconds=9.0)
    def abbiegen_callback(self): ###################################################### in Phasen unterteilen
        twist = Twist()
        if (self.get_clock().now() - self.timer_start).nanoseconds < 1500000000: #Phase 1 Deg-Kontrolle
            diff = (self.ziel_yaw - self.current_yaw + 540) % 360 - 180
            #self.get_logger().info(f"current-winkel: {self.current_yaw}, diff: {diff}")
            if self.richtung == "rechts":
                if -diff > 80.0:
                    twist.angular.z = -2.65
                elif -diff > 60.0:
                    twist.angular.z = -1.65
                elif -diff > 40.0:
                    twist.angular.z = -1.45
                elif -diff > 20.0:
                    twist.angular.z = -0.65
                elif -diff < 20.0:
                    twist.angular.z = 1.0
                else:
                    twist.angular.z = 0.0
                #twist.angular.z = -0.65 #ermittelte Richtwerte. Könnte je Roboter variieren. die Diff zwischen Beiden Motoren wird einfach Linear beachtet
            elif self.richtung == "links":
                if diff > 80.0:
                    twist.angular.z = 3.0
                elif diff > 60.0:
                    twist.angular.z = 2.0
                elif diff > 40.0:
                    twist.angular.z = 1.8
                elif diff > 20.0:
                    twist.angular.z = 1.0
                elif diff < 20.0:
                    twist.angular.z = -0.65
                else:
                    twist.angular.z = 0.0
                #twist.angular.z = 1.0
        elif (self.get_clock().now() - self.timer_start).nanoseconds < 5000000000: #Phase 2 Kamera-Kontrolle
            if self.contours_geradeaus:
                M = cv2.moments(max(self.contours_geradeaus, key=cv2.contourArea))
                if M and M['m00'] >= 100:
                    cx = int(M['m10'] / M['m00'])
                    center = self.breite // 2
                    error = cx - center
                    if error >= 40:
                        twist.angular.z = -error * 0.001
                    else:
                        #self.get_logger().info("Abbiegen beendet.")
                        self.kreuzung_rechts = False
                        self.kreuzung_links = False
                        self.State = "fahren"
                        #self.get_logger().info("STATEMACHINE: fahren")
                        self.timer.cancel()
                else:
                    self.get_logger().info("ERRORSTATE: konnte linie nicht ganz erkennen")
        elif (self.get_clock().now() - self.timer_start).nanoseconds < self.timer_dauer.nanoseconds: #Phase 3 abschließen
            if self.contours_geradeaus:
                M = cv2.moments(max(self.contours_geradeaus, key=cv2.contourArea))
                if M and M['m00'] >= 100:
                    cx = int(M['m10'] / M['m00'])
                    center = self.breite // 2
                    error = cx - center
                    if error <= self.threshold:
                        #self.get_logger().info("Abbiegen beendet.")
                        self.kreuzung_rechts = False
                        self.kreuzung_links = False
                        self.State = "fahren"
                        #self.get_logger().info("STATEMACHINE: fahren")
                        self.timer.cancel()
                    else: 
                        twist.angular.z = -error * 0.001
        else:#Timeout, sollte im Normalfall nicht passieren
            twist.angular.z = 0.0
            self.get_logger().info("Abbiegen fehlgeschlagen.")
            self.kreuzung_rechts = False
            self.kreuzung_links = False
            self.State = "ausrichten"
            self.get_logger().info("STATEMACHINE: ausrichten")
            self.timer.cancel()
        self.cmd_pub.publish(twist)

    def turn_asynchron(self):
        self.State = "waiting"
        self.erkennung = False
        self.ziel_yaw = (self.current_yaw + 180) % 360
        #self.get_logger().info(f"Zielwinkel: {self.ziel_yaw}") #debug
        self.timer = self.create_timer(0.05, self.turn_callback)
        self.timer_start = self.get_clock().now()
        self.timer_dauer = rclpy.duration.Duration(seconds=6.0)
    def turn_callback(self):
        twist = Twist()
        if (self.get_clock().now() - self.timer_start).nanoseconds < 2000000000: #Phase 1: Deg-Kontrolle
                diff = (self.ziel_yaw - self.current_yaw + 540) % 360 - 180
                #self.get_logger().info(f"current-winkel: {self.current_yaw}, diff: {diff}")
                if abs(diff) > 160.0:
                    twist.angular.z = 5.0
                elif diff > 100.0:
                    twist.angular.z = 2.0
                elif diff > 50.0:
                    twist.angular.z = 1.8
                elif diff > 10.0:
                    twist.angular.z = 1.0
                elif diff < 20.0:
                    twist.angular.z = -1.0
                else:
                    twist.angular.z = 0.0
        elif (self.get_clock().now() - self.timer_start).nanoseconds < 6000000000: #Phase 2: Kamera-Kontrolle
            if self.contours_geradeaus:
                M = cv2.moments(max(self.contours_geradeaus, key=cv2.contourArea))
                if M and M['m00'] >= 100:
                    cx = int(M['m10'] / M['m00'])
                    center = self.breite // 2
                    error = cx - center
                    if error >= 10:
                        twist.angular.z = -error * 0.001
                        twist.angular.x = -0.01
                    else: 
                        self.kreuzung_rechts = False
                        self.kreuzung_links = False
                        self.State = "fahren"
                        #self.get_logger().info("STATEMACHINE: fahren")
                        self.timer.cancel()
        else:
            twist.angular.z = 0.0
            self.get_logger().info("Wenden fehlgeschlagen.")
            self.kreuzung_rechts = False
            self.kreuzung_links = False
            self.State = "ausrichten"
            self.get_logger().info("STATEMACHINE: ausrichten")
            self.timer.cancel()
        self.cmd_pub.publish(twist)

    def close_gap_asynchron(self):
        self.State = "waiting"
        self.erkennung = True
        self.timer = self.create_timer(0.1, self.gap_callback)
        self.timer_start = self.get_clock().now()
        self.timer_dauer = rclpy.duration.Duration(seconds=1.5)
    def gap_callback(self):
        twist = Twist()
        if self.get_clock().now() - self.timer_start < self.timer_dauer:
            if self.linear_speed == 0.1:
                twist.linear.x = self.linear_speed
                twist.angular.z = 0.0
            else:
                twist.linear.x = 0.0
                twist.angular.z = 0.0
            self.cmd_pub.publish(twist)
        else:
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.cmd_pub.publish(twist)
            #self.get_logger().info("gap close beendet.")
            self.State = "abbiegen"
            #self.get_logger().info("STATEMACHINE: abbiegen")
            self.timer.cancel()

    def make_decision(self, decision):
        self.get_logger().info(f"Fall: {decision}-Abbiegung")
        if decision in ["links", "rechts"]:
            self.abbiegen_asynchron(decision)
        elif decision == "umkehren":
            self.turn_asynchron()

    def search_line(self, mode):
        self.mode = mode
        self.State = "waiting"
        self.erkennung = False
        self.best_pos = 10000000
        self.last_pos = 0
        self.last_error = 0
        self.timer = self.create_timer(0.2, self.line_callback)
        self.timer_start = self.get_clock().now()
        self.timer_dauer = rclpy.duration.Duration(seconds=8)
    def line_callback(self):
        if self.contours_geradeaus: #Dynamische Zustandserkennung
            self.mode = False
        else:
            self.mode = True
        twist = Twist()
        twist.linear.x = 0.0
        if self.get_clock().now() - self.timer_start < self.timer_dauer:
            if self.mode == False:### er sieht die Linie, muss nur nochmal feinjustieren
                    error = self.get_error()
                    if error and abs(error) < self.best_pos:
                        self.best_pos = abs(error)
                        if self.best_pos <= self.threshold: #ausreichend ausgerichtet
                            twist.angular.z = 0.0
                            self.cmd_pub.publish(twist)
                            self.get_logger().info("feinjustieren beendet")
                            self.State = "fahren"
                            self.get_logger().info("STATEMACHINE: fahren")
                            self.timer.cancel()
                            ##### ende #######
                        twist.angular.z = (-error * self.kj) / 2
                        self.last_error = twist.angular.z
                    else:### überdreht ###
                        twist.angular.z = (-self.last_error * self.kj) / 2
                        self.last_error = twist.angular.z
            else: #er muss die Linie erst einmal finden
                if (self.get_clock().now() - self.timer_start).nanoseconds < self.timer_dauer.nanoseconds / 2: # erst Hälfte der Zeit
                    twist.angular.z = 1.0
                    self.get_logger().info("searchline erste Hälfte")
                else:
                    twist.angular.z = -2.0
                    self.get_logger().info("searchline zweite Hälfte")
        else:#Timeout
            twist.linear.z = 0.0
            self.get_logger().info("search_line Timeout")
            self.State = "ausrichten"
            self.get_logger().info("STATEMACHINE: ausrichten")
            self.timer.cancel()
        self.cmd_pub.publish(twist)

    def get_mean_error(self):
        if len(self.error_queue) > 0:
            return np.mean(self.error_queue)
        else:
            return 0.0

    def get_error(self):
        M = cv2.moments(max(self.contours_geradeaus, key=cv2.contourArea))
        if M and M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            center = self.breite // 2
            return cx - center


    ###########################################################################################

    ###########################################################################################


def main(args=None):
    rclpy.init(args=args)
    node = PathfinderStream()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.picam2_0.stop()
        node.picam2_1.stop()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
