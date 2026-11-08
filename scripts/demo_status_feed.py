#!/usr/bin/env python3
"""Write the live task status to a small JSON file that the on-screen demo panel reads.

    python3 scripts/demo_status_feed.py [output.json]

Default output: /mnt/c/Users/Aorus15/AppData/Local/Temp/hcw_status.json (readable from Windows as
C:\\Users\\Aorus15\\AppData\\Local\\Temp\\hcw_status.json). Used by tools/demo_panel.py for the demo video.
Reads /hcw/task_status (task manager) and /perception/target_status (verifier). Read-only: publishes nothing.
"""
import json
import os
import sys
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

OUT = sys.argv[1] if len(sys.argv) > 1 else '/mnt/c/Users/Aorus15/AppData/Local/Temp/hcw_status.json'


class Feed(Node):
    def __init__(self):
        super().__init__('demo_status_feed')
        self.data = {'state': 'IDLE', 'result': 'IDLE', 'cause': '', 'point': '', 'task_id': 0,
                     'consecutive': 0, 'required': 5, 'detected_ids': [], 'expected_id': 0, 't': time.time(),
                     'outcome': '', 'fail_cause': '', 'reached': ''}
        self.create_subscription(String, '/hcw/task_status', self.on_task, 10)
        self.create_subscription(String, '/perception/target_status', self.on_target, 10)
        self.create_timer(0.25, self.write)

    def on_task(self, msg):
        try:
            s = json.loads(msg.data)
        except ValueError:
            return
        for k in ('state', 'result', 'cause', 'point', 'task_id'):
            self.data[k] = s.get(k, self.data.get(k))
        # remember how the task ended: FAILED is published only for an instant before RETURN_HOME follows
        state = s.get('state')
        if state == 'NAVIGATE_TO_POINT':
            self.data.update({'outcome': '', 'fail_cause': '', 'reached': state})
        elif state == 'FAILED':
            self.data.update({'outcome': 'failed', 'fail_cause': s.get('cause', '')})
        elif s.get('result') == 'COMPLETED':
            self.data['outcome'] = 'completed'
        if state not in ('FAILED', 'RETURN_HOME', 'IDLE', None):
            self.data['reached'] = state

    def on_target(self, msg):
        try:
            s = json.loads(msg.data)
        except ValueError:
            return
        self.data.update({'consecutive': s.get('consecutive', 0), 'detected_ids': s.get('detected_ids', []),
                          'expected_id': s.get('expected_id', 0)})

    def write(self):
        self.data['t'] = time.time()
        try:   # the Windows panel may be reading the file at this moment: skip this beat, try again at the next
            with open(OUT, 'w') as f:
                json.dump(self.data, f)
        except OSError:
            pass


def main():
    rclpy.init()
    rclpy.spin(Feed())


if __name__ == '__main__':
    main()
