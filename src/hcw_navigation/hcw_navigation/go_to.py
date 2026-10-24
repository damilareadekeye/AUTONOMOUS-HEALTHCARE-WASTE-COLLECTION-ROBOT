"""Send the robot to named places from hcw_world/config/locations.yaml.

    ros2 run hcw_navigation go_to collection_A
    ros2 run hcw_navigation go_to collection_A collection_B storage home     # in order

Needs the simulation and `ros2 launch hcw_navigation navigation.launch.py` running.
Exit code is 0 only if every place was reached.
"""
import math
import sys

import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import os


def load_locations():
    path = os.path.join(get_package_share_directory('hcw_world'), 'config', 'locations.yaml')
    with open(path) as f:
        return yaml.safe_load(f)['locations']


def pose(navigator, loc):
    p = PoseStamped()
    p.header.frame_id = 'map'
    p.header.stamp = navigator.get_clock().now().to_msg()
    p.pose.position.x, p.pose.position.y = float(loc['x']), float(loc['y'])
    p.pose.orientation.z = math.sin(loc['yaw'] / 2)
    p.pose.orientation.w = math.cos(loc['yaw'] / 2)
    return p


def go_to(navigator, name, loc, timeout_s=300.0):
    """Drive to one named place. Returns True on success."""
    navigator.goToPose(pose(navigator, loc))
    start = navigator.get_clock().now()
    while not navigator.isTaskComplete():
        if (navigator.get_clock().now() - start).nanoseconds / 1e9 > timeout_s:
            navigator.cancelTask()
            break
    result = navigator.getResult()
    print('%-14s %s' % (name, 'reached' if result == TaskResult.SUCCEEDED else 'FAILED (%s)' % result))
    return result == TaskResult.SUCCEEDED


def main():
    locations = load_locations()
    names = sys.argv[1:]
    if not names or any(n not in locations for n in names):
        print('usage: go_to <place> [<place> ...]   places: %s' % ', '.join(locations))
        sys.exit(2)
    rclpy.init()
    navigator = BasicNavigator()
    # localizer='bt_navigator': the default ('amcl') would publish a (0, 0) initial pose and reset
    # AMCL. The start pose is set once by Nav2 itself (amcl.initial_pose in nav2_params.yaml).
    navigator.waitUntilNav2Active(localizer='bt_navigator')
    ok = all(go_to(navigator, n, locations[n]) for n in names)
    rclpy.shutdown()
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
