"""Task manager: the state machine of docs/07_Task_Manager_Design.md.

    ros2 run hcw_task request A              # ask for a collection from point A (see request.py)

IDLE -> NAVIGATE_TO_POINT -> VERIFY -> ATTACH -> NAVIGATE_TO_STORAGE -> RELEASE -> REPORT -> RETURN_HOME -> IDLE
A failure (navigation, wrong or missing container, magnet) ends in FAILED, which puts the container back,
returns the robot home and goes to IDLE. Motion is done only by Nav2; this node never publishes velocities.

  in   /hcw/task_request          std_msgs/String   "A", "B" or "C"
  in   /perception/target_status  std_msgs/String   JSON from the verifier
  in   /magnet/status             std_msgs/String
  out  /hcw/task_status           std_msgs/String   JSON {task_id, state, point, result, cause, times...}
  out  /perception/expected_tag   std_msgs/Int32
  out  /magnet/command            std_msgs/String
"""
import csv
import json
import math
import os
import subprocess
import time

import cv2
import numpy as np
import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from std_msgs.msg import Int32, String

POINTS = {'A': 'collection_A', 'B': 'collection_B', 'C': 'collection_C'}
VERIFY_TIMEOUT = 10.0      # s to wait for VERIFIED per attempt
VERIFY_ATTEMPTS = 3
VERIFY_WAIT = 3.0          # s between attempts
NAV_TIMEOUT = 360.0        # s per navigation goal
CSV_COLUMNS = ['run_id', 'date', 'collection_point', 'wrong_container', 'obstacle', 'success', 'time_navigate_s',
               'time_verify_s', 'time_transport_s', 'failure_cause', 'notes']


def load_config():
    path = os.path.join(get_package_share_directory('hcw_world'), 'config', 'locations.yaml')
    with open(path) as f:
        return yaml.safe_load(f)


class TaskManager(Node):
    def __init__(self):
        super().__init__('task_manager')
        self.declare_parameter('wrong_container', False)   # test labels for the CSV only
        self.declare_parameter('obstacle', False)
        self.declare_parameter('notes', '')
        # True: put the requested container back at its place at the start of each task. Set to false
        # (ros2 param set /task_manager reset_container false) to test a missing or a wrong container.
        self.declare_parameter('reset_container', True)
        self.cfg = load_config()
        self.locations = self.cfg['locations']
        self.drop = self.cfg['drop_points']['storage']
        self.queue = []
        self.busy = False
        self.task_id = self.last_run_id()          # continue the numbering of earlier sessions
        self.target = {}
        self.magnet_status = ''
        self.status_pub = self.create_publisher(String, '/hcw/task_status', 10)
        self.expected_pub = self.create_publisher(Int32, '/perception/expected_tag', 10)
        self.magnet_pub = self.create_publisher(String, '/magnet/command', 10)
        self.create_subscription(String, '/hcw/task_request', self.on_request, 10)
        self.create_subscription(String, '/perception/target_status', self.on_target, 10)
        self.create_subscription(String, '/magnet/status', self.on_magnet, 10)
        self.last_image = None
        self.amcl = {}
        self.create_subscription(Image, '/rgbd_camera/image', self.on_image, qos_profile_sensor_data)
        self.create_subscription(PoseWithCovarianceStamped, '/amcl_pose', self.on_amcl, 10)
        self.navigator = BasicNavigator()
        self.info = {}

    @staticmethod
    def last_run_id():
        path = os.path.expanduser('~/hcw_ws/results/runs.csv')
        try:
            with open(path, newline='') as f:
                rows = list(csv.reader(f))[1:]
            return max(int(r[0]) for r in rows) if rows else 0
        except (OSError, ValueError, IndexError):
            return 0

    # ------------------------------------------------------------ callbacks
    def on_request(self, msg):
        point = msg.data.strip().upper()
        if point not in POINTS:
            return self.publish_status('IDLE', 'REJECTED', 'invalid request "%s" (use A, B or C)' % msg.data, point=point)
        if self.busy or self.queue:
            return self.publish_status('BUSY', 'REJECTED', 'a task is already running', point=point)
        self.queue.append(point)

    def on_image(self, msg):
        self.last_image = msg

    def on_amcl(self, msg):
        p = msg.pose.pose
        q = p.orientation
        self.amcl = {'x': round(p.position.x, 3), 'y': round(p.position.y, 3),
                     'yaw': round(math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z)), 3)}

    def on_target(self, msg):
        try:
            self.target = json.loads(msg.data)
        except ValueError:
            pass

    def on_magnet(self, msg):
        self.magnet_status = msg.data

    # ------------------------------------------------------------ helpers
    def now(self):
        return self.get_clock().now().nanoseconds / 1e9

    def spin_for(self, seconds):
        end = self.now() + seconds
        while self.now() < end and rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.05)

    def wait_until(self, predicate, timeout):
        end = self.now() + timeout
        while self.now() < end and rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.05)
            if predicate():
                return True
        return predicate()

    def publish_status(self, state, result='RUNNING', cause='', point=None, **extra):
        body = {'task_id': self.task_id, 'state': state, 'point': point or self.info.get('point', ''),
                'result': result, 'cause': cause}
        body.update(extra)
        self.status_pub.publish(String(data=json.dumps(body)))
        self.get_logger().info('%s %s %s' % (state, result, cause))

    def magnet(self, command, expect, timeout=4.0):
        self.magnet_status = ''
        self.magnet_pub.publish(String(data=command))
        ok = self.wait_until(lambda: self.magnet_status.startswith(expect) or self.magnet_status.startswith('error'), timeout)
        return ok and self.magnet_status.startswith(expect), self.magnet_status

    def navigate(self, name):
        """Drive to a named place with Nav2. True on success."""
        loc = self.locations[name]
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.navigator.get_clock().now().to_msg()
        pose.pose.position.x, pose.pose.position.y = float(loc['x']), float(loc['y'])
        pose.pose.orientation.z, pose.pose.orientation.w = math.sin(loc['yaw'] / 2), math.cos(loc['yaw'] / 2)
        self.navigator.goToPose(pose)
        start = self.now()
        while not self.navigator.isTaskComplete():
            rclpy.spin_once(self, timeout_sec=0.05)
            if self.now() - start > NAV_TIMEOUT:
                self.navigator.cancelTask()
                break
        return self.navigator.getResult() == TaskResult.SUCCEEDED

    def save_incident(self, tag, cause):
        """When verification fails, keep evidence: camera frame, robot pose, container position, tag status.

        Written to ~/hcw_ws/results/incidents/task_<id>_<time>/ (not committed). Never raises.
        """
        try:
            folder = os.path.expanduser('~/hcw_ws/results/incidents/task_%d_%s' % (self.task_id, time.strftime('%H%M%S')))
            os.makedirs(folder, exist_ok=True)
            info = {'task_id': self.task_id, 'point': self.info.get('point'), 'cause': cause,
                    'expected_tag': tag, 'target_status': self.target, 'amcl_pose': self.amcl}
            out = subprocess.run(['gz', 'model', '-m', 'hcw_container_%d' % tag, '-p'], capture_output=True,
                                 text=True, timeout=8)
            info['container_pose_in_gazebo'] = out.stdout.strip()
            with open(os.path.join(folder, 'incident.json'), 'w') as f:
                json.dump(info, f, indent=2)
            if self.last_image is not None:
                m = self.last_image
                img = np.frombuffer(m.data, np.uint8).reshape(m.height, m.width, -1)
                cv2.imwrite(os.path.join(folder, 'camera.png'),
                            cv2.cvtColor(img, cv2.COLOR_RGB2BGR) if m.encoding == 'rgb8' else img)
            self.get_logger().info('incident saved in %s' % folder)
        except Exception as e:  # diagnostics must never break a task
            self.get_logger().warn('could not save incident: %s' % e)

    def log_csv(self, success, cause, t_nav, t_verify, t_transport):
        folder = os.path.expanduser('~/hcw_ws/results')
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, 'runs.csv')
        new = not os.path.exists(path)
        with open(path, 'a', newline='') as f:
            w = csv.writer(f)
            if new:
                w.writerow(CSV_COLUMNS)
            w.writerow([self.task_id, time.strftime('%Y-%m-%d %H:%M:%S'), self.info['point'],
                        'yes' if self.get_parameter('wrong_container').value else 'no',
                        'yes' if self.get_parameter('obstacle').value else 'no',
                        'yes' if success else 'no', round(t_nav, 1), round(t_verify, 1), round(t_transport, 1),
                        cause, self.get_parameter('notes').value])

    # ------------------------------------------------------------ the task
    def run_task(self, point):
        self.busy = True
        self.task_id += 1
        place = POINTS[point]
        tag = int(self.locations[place]['tag_id'])
        self.info = {'point': point}
        t_nav = t_verify = t_transport = 0.0
        attached = False

        def fail(cause):
            nonlocal attached
            self.publish_status('FAILED', 'FAILED', cause)
            self.expected_pub.publish(Int32(data=0))
            if attached:
                self.magnet('reset:%d' % tag, 'reset')
            self.log_csv(False, cause, t_nav, t_verify, t_transport)
            self.go_home()

        self.expected_pub.publish(Int32(data=0))
        if self.get_parameter('reset_container').value:
            self.magnet('reset:%d' % tag, 'reset')                  # container back at its place

        # 1. drive to the collection point
        self.publish_status('NAVIGATE_TO_POINT')
        t0 = self.now()
        if not self.navigate(place):
            t_nav = self.now() - t0
            return fail('navigation to the collection point failed')
        t_nav = self.now() - t0

        # 2. verify the container (expected tag seen consistently, no other tag)
        t0 = self.now()
        verified, wrong = False, False
        for attempt in range(1, VERIFY_ATTEMPTS + 1):
            self.publish_status('VERIFY', cause='attempt %d of %d' % (attempt, VERIFY_ATTEMPTS))
            self.expected_pub.publish(Int32(data=tag))
            verified = self.wait_until(lambda: bool(self.target.get('verified')), VERIFY_TIMEOUT)
            if verified:
                break
            ids = self.target.get('detected_ids', [])
            wrong = bool([i for i in ids if i != tag])
            self.spin_for(VERIFY_WAIT)
        t_verify = self.now() - t0
        self.expected_pub.publish(Int32(data=0))
        if not verified:
            self.save_incident(tag, 'verification failed')
            return fail('wrong container (tag(s) %s seen, expected %d)' % (self.target.get('detected_ids'), tag)
                        if wrong else 'no container tag detected (expected %d)' % tag)

        # 3. magnet attaches the container
        self.publish_status('ATTACH')
        ok, text = self.magnet('attach:%d' % tag, 'attached')
        if not ok:
            return fail('magnet failed to attach: %s' % text)
        attached = True

        # 4. transport to storage
        self.publish_status('NAVIGATE_TO_STORAGE')
        t0 = self.now()
        if not self.navigate('storage'):
            t_transport = self.now() - t0
            return fail('navigation to storage failed')
        t_transport = self.now() - t0

        # 5. release
        self.publish_status('RELEASE')
        ok, text = self.magnet('release:%s,%s,%s' % (self.drop['x'], self.drop['y'], self.drop['yaw']), 'released')
        if not ok:
            return fail('magnet failed to release: %s' % text)
        attached = False

        # 6. report, 7. go home
        self.publish_status('REPORT', 'COMPLETED', '', time_navigate_s=round(t_nav, 1),
                            time_verify_s=round(t_verify, 1), time_transport_s=round(t_transport, 1))
        self.log_csv(True, '', t_nav, t_verify, t_transport)
        self.go_home()

    def go_home(self):
        self.publish_status('RETURN_HOME')
        if not self.navigate('home'):
            self.publish_status('RETURN_HOME', 'FAILED', 'could not return home')
        self.busy = False
        self.publish_status('IDLE', 'IDLE')


def main():
    rclpy.init()
    node = TaskManager()
    node.navigator.waitUntilNav2Active(localizer='bt_navigator')
    node.get_logger().info('task manager ready: publish "A", "B" or "C" on /hcw/task_request')
    node.publish_status('IDLE', 'IDLE')
    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.2)
            if node.queue:
                node.run_task(node.queue.pop(0))
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
