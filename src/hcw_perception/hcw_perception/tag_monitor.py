"""Show which AprilTag ids the camera sees (a quick check that detection works).

    ros2 run hcw_perception tag_monitor              # print changes until Ctrl+C
    ros2 run hcw_perception tag_monitor --collect 6  # listen 6 s, print the ids seen, exit

With --collect the output is one line: the ids seen (sorted, space separated) or `none`.
"""
import sys

import rclpy
from apriltag_msgs.msg import AprilTagDetectionArray
from rclpy.node import Node


class TagMonitor(Node):
    def __init__(self):
        super().__init__('tag_monitor')
        self.create_subscription(AprilTagDetectionArray, '/detections', self.on_detections, 10)
        self.last = None
        self.seen = set()

    def on_detections(self, msg):
        ids = sorted(d.id for d in msg.detections)
        self.seen.update(ids)
        if ids != self.last:
            self.get_logger().info('tags seen: %s' % (ids if ids else 'none'))
            self.last = ids


def main():
    rclpy.init()
    node = TagMonitor()
    if '--collect' in sys.argv:
        seconds = float(sys.argv[sys.argv.index('--collect') + 1])
        end = node.get_clock().now().nanoseconds + seconds * 1e9
        while node.get_clock().now().nanoseconds < end:
            rclpy.spin_once(node, timeout_sec=0.1)
        print(' '.join(str(i) for i in sorted(node.seen)) or 'none')
        rclpy.shutdown()
        return
    rclpy.spin(node)


if __name__ == '__main__':
    main()
