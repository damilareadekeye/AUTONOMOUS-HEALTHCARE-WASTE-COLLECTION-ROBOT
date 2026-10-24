"""Print the tag ids the camera currently sees (a quick check that detection works).

    ros2 run hcw_perception tag_monitor
"""
import rclpy
from apriltag_msgs.msg import AprilTagDetectionArray
from rclpy.node import Node


class TagMonitor(Node):
    def __init__(self):
        super().__init__('tag_monitor')
        self.create_subscription(AprilTagDetectionArray, '/detections', self.on_detections, 10)
        self.last = None

    def on_detections(self, msg):
        ids = sorted(d.id for d in msg.detections)
        if ids != self.last:
            self.get_logger().info('tags seen: %s' % (ids if ids else 'none'))
            self.last = ids


def main():
    rclpy.init()
    rclpy.spin(TagMonitor())


if __name__ == '__main__':
    main()
