"""Decide whether the expected container tag is VERIFIED.

Rule (docs/07_Task_Manager_Design.md): the expected tag is seen, and no other tag, in `required_frames`
consecutive detection messages. A single noisy detection never verifies.

Topics
  in   /detections                  apriltag_msgs/AprilTagDetectionArray   (from apriltag_ros)
  in   /perception/expected_tag      std_msgs/Int32     tag id to look for, 0 = not looking
  out  /perception/target_status     std_msgs/String    JSON, published on every detection message and at 2 Hz

This node only observes. It never publishes motor commands.
"""
import json

import rclpy
from apriltag_msgs.msg import AprilTagDetectionArray
from rclpy.node import Node
from std_msgs.msg import Int32, String


class Verifier(Node):
    def __init__(self):
        super().__init__('verifier')
        self.declare_parameter('required_frames', 5)
        self.required = int(self.get_parameter('required_frames').value)
        self.expected = 0
        self.consecutive = 0
        self.detected_ids = []
        self.pub = self.create_publisher(String, '/perception/target_status', 10)
        self.create_subscription(Int32, '/perception/expected_tag', self.on_expected, 10)
        self.create_subscription(AprilTagDetectionArray, '/detections', self.on_detections, 10)
        self.create_timer(0.5, self.publish)

    def on_expected(self, msg):
        if msg.data != self.expected:
            self.expected = msg.data
            self.consecutive = 0
            self.get_logger().info('expected tag: %s' % (self.expected or 'none'))

    def on_detections(self, msg):
        self.detected_ids = sorted(d.id for d in msg.detections)
        if self.expected and self.detected_ids == [self.expected]:
            self.consecutive += 1
        else:
            self.consecutive = 0
        self.publish()

    def publish(self):
        out = String()
        out.data = json.dumps({
            'expected_id': self.expected,
            'detected_ids': self.detected_ids,
            'detected': bool(self.detected_ids),
            'consecutive': self.consecutive,
            'verified': bool(self.expected) and self.consecutive >= self.required,
            'stamp': self.get_clock().now().nanoseconds / 1e9,
        })
        self.pub.publish(out)


def main():
    rclpy.init()
    rclpy.spin(Verifier())


if __name__ == '__main__':
    main()
