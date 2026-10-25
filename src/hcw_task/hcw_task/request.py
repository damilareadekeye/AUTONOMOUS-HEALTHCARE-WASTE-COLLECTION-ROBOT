"""Ask the task manager for a collection and watch it run.

    ros2 run hcw_task request A            # one task
    ros2 run hcw_task request A B C        # three tasks, one after the other

Prints every state change. Exit code 0 only if every task COMPLETED.
"""
import json
import sys
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

DONE = ('COMPLETED', 'FAILED', 'REJECTED')


class Requester(Node):
    def __init__(self):
        super().__init__('task_requester')
        self.pub = self.create_publisher(String, '/hcw/task_request', 10)
        self.create_subscription(String, '/hcw/task_status', self.on_status, 10)
        self.last = None
        self.result = None

    def on_status(self, msg):
        s = json.loads(msg.data)
        line = '%-22s %-9s %s' % (s['state'], s['result'], s.get('cause', ''))
        if line != self.last:
            print('[task %s %s] %s' % (s['task_id'], s.get('point', ''), line), flush=True)
            self.last = line
        if s['result'] in DONE and s['state'] in ('REPORT', 'FAILED', 'IDLE') and self.active:
            if s['result'] in ('COMPLETED', 'REJECTED', 'FAILED'):
                self.result = s['result']

    active = False


def main():
    points = [p.upper() for p in sys.argv[1:]]
    if not points:
        print('usage: request A [B C ...]')
        return 2
    rclpy.init()
    node = Requester()
    end = time.time() + 20
    while node.pub.get_subscription_count() == 0 and time.time() < end:
        rclpy.spin_once(node, timeout_sec=0.2)
    if node.pub.get_subscription_count() == 0:
        print('task manager is not running (no one listens on /hcw/task_request)')
        return 1
    all_ok = True
    for p in points:
        node.result, node.active = None, True
        node.pub.publish(String(data=p))
        end = time.time() + 900
        while node.result is None and time.time() < end:
            rclpy.spin_once(node, timeout_sec=0.2)
        # wait until the robot is back home and idle before the next task
        node.last = None
        idle_end = time.time() + 600
        while time.time() < idle_end:
            rclpy.spin_once(node, timeout_sec=0.2)
            if node.last and node.last.startswith('IDLE'):
                break
        all_ok = all_ok and node.result == 'COMPLETED'
        node.active = False
    rclpy.shutdown()
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
