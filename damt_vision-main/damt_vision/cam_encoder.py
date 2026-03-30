#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from picamera2 import Picamera2
import numpy as np
import cv2

class PathfinderStream(Node):
    def __init__(self):
        super().__init__('pathfinder_stream')

        self.publisher_ = self.create_publisher(CompressedImage, '/camera/image/compressed', 1)
        self.timer = self.create_timer(0.1, self.capture_and_publish)

        # Kamera Setup
        self.video_w, self.video_h = 1920, 1080
        self.lo_w, self.lo_h = 1920, 1080
        self.picam2_0 = Picamera2(camera_num=0)
        self.picam2_1 = Picamera2(camera_num=1)

        main_config = {'size': (self.video_w, self.video_h), 'format': 'XRGB8888'}
        lores_config = {'size': (self.lo_w, self.lo_h), 'format': 'YUV420'}
        controls = {'FrameRate': 30}

        config_0 = self.picam2_0.create_video_configuration(main_config, lores=lores_config, buffer_count=2, controls=controls)
        config_1 = self.picam2_1.create_video_configuration(main_config, lores=lores_config, buffer_count=2, controls=controls)

        self.picam2_0.configure(config_0)
        self.picam2_1.configure(config_1)
        self.picam2_0.start()
        self.picam2_1.start()

    def capture_and_publish(self):
        frame_0 = self.picam2_0.capture_array('main')
        frame_1 = self.picam2_1.capture_array('main')

        height = 200
        width = 1344
        y_start, y_end = self.video_h - height, self.video_h
        x_start_0, x_end_0 = 0, width
        x_start_1, x_end_1 = self.video_w - width, self.video_w

        cropped_0 = frame_0[y_start:y_end, x_start_0:x_end_0]
        cropped_1 = frame_1[y_start:y_end, x_start_1:x_end_1]

        cropped_light_0 = frame_0[:, x_start_0+200:x_end_0]
        cropped_light_1 = frame_1[:, x_start_1:x_end_1-200]

        stitched = np.hstack((cropped_light_0, cropped_light_1))

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        success, encoded_image = cv2.imencode('.jpg', stitched, encode_param)

        if success:
            msg = CompressedImage()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.format = "jpeg"
            msg.data = encoded_image.tobytes()
            self.publisher_.publish(msg)
        else:
            self.get_logger().error("Image encoding failed")

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
