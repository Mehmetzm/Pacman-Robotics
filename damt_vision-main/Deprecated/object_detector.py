#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from geometry_msgs.msg import Twist
from std_msgs.msg import String
import numpy as np
import cv2
import os
import random
import json
    

    
class ObjectDetector(Node):
    def __init__(self):
        super().__init__('object_detector')
        self.bridge = CvBridge()

        # Abonniert Kamera-Feed
        self.sub = self.create_subscription(
            CompressedImage,
            '/camera/image/compressed',
            self.image_callback,
            10
        )

        # Publisher für annotiertes Bild
        self.pub = self.create_publisher(
            CompressedImage,
            '/camera/image/annotated/compressed',
            10
        )

        # Farbbereiche in HSV für die Erkennung (kannst du anpassen)
        self.hsv_ranges = {
            'pacdot': ((20, 100, 100), (35, 255, 255)),             # Gelb
            'cherry': ((0, 100, 100), (10, 255, 255)),              # Rot
            'ghost_vulnerable': ((90, 100, 100), (110, 255, 255)), # Hellblau / Cyan
        }

        # Farben für die Bounding Boxen 
        self.color_map = {
            'pacdot': (0, 255, 255),            # Gelb
            'cherry': (0, 0, 255),              # Rot
            'ghost_vulnerable': (255, 200, 150) # Hellblau
        }

    def image_callback(self, msg):
        # CompressedImage → OpenCV-Bild
        np_arr = np.frombuffer(msg.data, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if image is None:
            self.get_logger().warn("Fehler beim Bilddecodieren.")
            return

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        for label, (lower, upper) in self.hsv_ranges.items():
            lower_np = np.array(lower)
            upper_np = np.array(upper)

            # Maske für bestimmte Farbe
            mask = cv2.inRange(hsv, lower_np, upper_np)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                if cv2.contourArea(cnt) < 100:  # Kleine Punkte ignorieren
                    continue
                 
                x, y, w, h = cv2.boundingRect(cnt)

                self.get_logger().info(f"{label} erkannt")
                
                # Box zeichnen
                color = self.color_map.get(label, (255, 255, 255))
                cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)

                # Label-Hintergrund
                text_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                text_w, text_h = text_size
                cv2.rectangle(image, (x, y - text_h - 5), (x + text_w, y), color, -1)

                # Label-Text
                cv2.putText(image, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        # Anzeige (zum Debuggen)
        cv2.imshow("Object Detection", image)
        cv2.waitKey(1)

        # Rückveröffentlichung des annotierten Bildes
        _, buffer = cv2.imencode('.jpg', image)
        out_msg = CompressedImage()
        out_msg.format = 'jpeg'
        out_msg.data = np.array(buffer).tobytes()
        self.pub.publish(out_msg)


def main(args=None):
    rclpy.init(args=args)
    node = ObjectDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()