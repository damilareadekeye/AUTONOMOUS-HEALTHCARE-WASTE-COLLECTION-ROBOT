"""Drive the robot with the arrow keys.

    ros2 run hcw_bringup teleop_arrows

Up / Down      forward / backward        Left / Right   turn left / right
Space          stop                      + / -          faster / slower
q              quit

Hold a key to keep moving; the robot stops about half a second after you let go.
Click inside this terminal first: it only reads keys from its own window.
"""
import select
import sys
import termios
import tty

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node

HOLD_TIMEOUT = 0.5      # s without a key press before the robot stops
PUBLISH_PERIOD = 0.1    # s
SPEED_STEP = 1.2        # factor for + / -

# Arrow keys arrive as ESC [ A/B/C/D (or ESC O A/B/C/D in some terminals).
ARROWS = {'A': (1.0, 0.0), 'B': (-1.0, 0.0), 'C': (0.0, -1.0), 'D': (0.0, 1.0)}


class TeleopArrows(Node):
    def __init__(self):
        super().__init__('teleop_arrows')
        self.pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.linear = 0.3     # m/s
        self.angular = 0.8    # rad/s
        self.command = (0.0, 0.0)
        self.last_key_time = self.get_clock().now()
        self.create_timer(PUBLISH_PERIOD, self.publish)

    def set_command(self, direction):
        self.command = direction
        self.last_key_time = self.get_clock().now()

    def publish(self):
        age = (self.get_clock().now() - self.last_key_time).nanoseconds / 1e9
        x, w = self.command if age < HOLD_TIMEOUT else (0.0, 0.0)
        msg = Twist()
        msg.linear.x = x * self.linear
        msg.angular.z = w * self.angular
        self.pub.publish(msg)

    def change_speed(self, factor):
        self.linear = min(max(self.linear * factor, 0.05), 1.0)
        self.angular = min(max(self.angular * factor, 0.1), 2.0)
        print('\rspeed: %.2f m/s, %.2f rad/s      ' % (self.linear, self.angular), end='\r\n')


def read_key(timeout):
    """Return one key press ('' on timeout). Arrow keys return 'A','B','C','D' after an escape."""
    if not select.select([sys.stdin], [], [], timeout)[0]:
        return ''
    ch = sys.stdin.read(1)
    if ch == '\x1b':
        if select.select([sys.stdin], [], [], 0.05)[0]:
            seq = sys.stdin.read(2)           # '[A' or 'OA'
            return 'ARROW' + seq[-1]
        return ''
    return ch


def main():
    if not sys.stdin.isatty():
        print('teleop_arrows must be run in a terminal.')
        return
    rclpy.init()
    node = TeleopArrows()
    settings = termios.tcgetattr(sys.stdin)
    print(__doc__)
    try:
        tty.setcbreak(sys.stdin.fileno())
        while rclpy.ok():
            key = read_key(0.05)
            if key.startswith('ARROW') and key[-1] in ARROWS:
                node.set_command(ARROWS[key[-1]])
            elif key == ' ':
                node.set_command((0.0, 0.0))
            elif key in ('+', '='):
                node.change_speed(SPEED_STEP)
            elif key in ('-', '_'):
                node.change_speed(1 / SPEED_STEP)
            elif key in ('q', '\x03'):
                break
            rclpy.spin_once(node, timeout_sec=0)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.pub.publish(Twist())     # make sure the robot stops
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
