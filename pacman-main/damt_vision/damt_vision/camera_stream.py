#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge
from picamera2 import Picamera2
import cv2
import numpy as np

class DualCameraStream(Node):
    def __init__(self):
        super().__init__('dual_camera_stream_node')

        # Zwei Publisher – für Kamera 0 und 1
        self.publisher_cam0 = self.create_publisher(CompressedImage, '/camera0/image/compressed', 10)
        self.publisher_cam1 = self.create_publisher(CompressedImage, '/camera1/image/compressed', 10)

        self.timer = self.create_timer(0.2, self.publish_images)  # 10 Hz
        self.br = CvBridge()

        self.video_w, self.video_h = 1280, 720
        self.lo_w, self.lo_h = 1280, 720

        # Kameras initialisieren
        self.picam2_0 = Picamera2(camera_num=0)
        self.picam2_1 = Picamera2(camera_num=1)

        main_config = {'size': (self.video_w, self.video_h), 'format': 'XRGB8888'}
        lores_config = {'size': (self.lo_w, self.lo_h), 'format': 'YUV420'}
        controls = {'FrameRate': 15}

        config_0 = self.picam2_0.create_video_configuration(main_config, lores=lores_config, buffer_count=2, controls=controls)
        config_1 = self.picam2_1.create_video_configuration(main_config, lores=lores_config, buffer_count=2, controls=controls)

        self.picam2_0.configure(config_0)
        self.picam2_1.configure(config_1)

        self.picam2_0.start()
        self.picam2_1.start()

    def publish_images(self):
        frame_0 = self.picam2_0.capture_array('main')
        frame_1 = self.picam2_1.capture_array('main')

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]

        # Kamera 0
        success0, encoded0 = cv2.imencode('.jpg', frame_0, encode_param)
        if success0:
            msg0 = CompressedImage()
            msg0.header.stamp = self.get_clock().now().to_msg()
            msg0.header.frame_id = "camera0_frame"
            msg0.format = "jpeg"
            msg0.data = encoded0.tobytes()
            self.publisher_cam0.publish(msg0)

        # Kamera 1
        success1, encoded1 = cv2.imencode('.jpg', frame_1, encode_param)
        if success1:
            msg1 = CompressedImage()
            msg1.header.stamp = self.get_clock().now().to_msg()
            msg1.header.frame_id = "camera1_frame"
            msg1.format = "jpeg"
            msg1.data = encoded1.tobytes()
            self.publisher_cam1.publish(msg1)

    def stop_cameras(self):
        self.picam2_0.stop()
        self.picam2_1.stop()

def main(args=None):
    rclpy.init(args=args)
    node = DualCameraStream()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_cameras()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
