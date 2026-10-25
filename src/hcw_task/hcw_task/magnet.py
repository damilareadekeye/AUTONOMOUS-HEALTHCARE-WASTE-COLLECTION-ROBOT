"""Simulated magnet: the container model follows the robot while attached.

In the real robot this would be an electromagnet latch. In Gazebo the container model is moved
with the `set_pose` service (bridged to ROS), which is simple and reliable. Details: docs/07_Task_Manager_Design.md.

  in   /magnet/command   std_msgs/String   attach:<tag_id> | release:<x>,<y>,<yaw> | reset:<tag_id> | reset:all
  out  /magnet/status    std_msgs/String   attached:<tag_id> | released | reset | error:<text>

Attach only works within `magnet_range` metres of the container's home position (the robot must have
driven up to it). While attached the container is carried above the robot, higher than the LiDAR
plane so it does not appear as an obstacle to Nav2.
"""
import math
import os

import rclpy
import tf2_ros
import yaml
from ament_index_python.packages import get_package_share_directory
from rclpy.node import Node
from ros_gz_interfaces.msg import Entity
from ros_gz_interfaces.srv import SetEntityPose
from std_msgs.msg import String


def load_containers():
    path = os.path.join(get_package_share_directory('hcw_world'), 'config', 'locations.yaml')
    with open(path) as f:
        return {c['tag_id']: c for c in yaml.safe_load(f)['containers']}


def yaw_quaternion(yaw):
    return 0.0, 0.0, math.sin(yaw / 2), math.cos(yaw / 2)


class Magnet(Node):
    def __init__(self):
        super().__init__('magnet')
        self.declare_parameter('magnet_range', 2.5)      # m between robot and the container's home position
        self.declare_parameter('carry_height', 0.45)     # m: container origin above the floor while carried
        self.range = float(self.get_parameter('magnet_range').value)
        self.carry_z = float(self.get_parameter('carry_height').value)
        self.containers = load_containers()
        self.attached = None                              # tag id being carried
        self.pending = False
        self.tf_buffer = tf2_ros.Buffer()
        tf2_ros.TransformListener(self.tf_buffer, self)
        self.client = self.create_client(SetEntityPose, '/world/sim_world/set_pose')
        self.status = self.create_publisher(String, '/magnet/status', 10)
        self.create_subscription(String, '/magnet/command', self.on_command, 10)
        self.create_timer(0.1, self.follow)

    # ---- helpers
    def say(self, text):
        self.get_logger().info(text)
        self.status.publish(String(data=text))

    def robot_pose(self):
        try:
            t = self.tf_buffer.lookup_transform('map', 'base_link', rclpy.time.Time())
        except Exception:
            return None
        q = t.transform.rotation
        yaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
        return t.transform.translation.x, t.transform.translation.y, yaw

    def set_pose(self, tag_id, x, y, z, yaw):
        if not self.client.service_is_ready():
            return False
        req = SetEntityPose.Request()
        req.entity = Entity(name='hcw_container_%d' % tag_id, type=Entity.MODEL)
        req.pose.position.x, req.pose.position.y, req.pose.position.z = float(x), float(y), float(z)
        qx, qy, qz, qw = yaw_quaternion(yaw)
        req.pose.orientation.x, req.pose.orientation.y = qx, qy
        req.pose.orientation.z, req.pose.orientation.w = qz, qw
        return self.client.call_async(req)

    # ---- commands
    def on_command(self, msg):
        cmd, _, arg = msg.data.partition(':')
        try:
            if cmd == 'attach':
                self.attach(int(arg))
            elif cmd == 'release':
                x, y, yaw = (float(v) for v in arg.split(','))
                self.release(x, y, yaw)
            elif cmd == 'reset':
                self.reset(None if arg == 'all' else int(arg))
            else:
                self.say('error:unknown command %s' % msg.data)
        except (ValueError, KeyError) as e:
            self.say('error:bad command %s (%s)' % (msg.data, e))

    def attach(self, tag_id):
        if tag_id not in self.containers:
            return self.say('error:no container with tag %d' % tag_id)
        pose = self.robot_pose()
        if pose is None:
            return self.say('error:robot pose not available')
        c = self.containers[tag_id]
        dist = math.dist(pose[:2], (c['x'], c['y']))
        if dist > self.range:
            return self.say('error:container %d is %.1f m away (magnet range %.1f m)' % (tag_id, dist, self.range))
        self.attached = tag_id
        self.say('attached:%d' % tag_id)

    def release(self, x, y, yaw):
        if self.attached is None:
            return self.say('error:nothing attached')
        tag = self.attached
        self.attached = None
        self.set_pose(tag, x, y, 0.0, yaw)
        self.say('released')

    def reset(self, tag_id):
        if tag_id is None:
            self.attached = None
        elif self.attached == tag_id:
            self.attached = None
        for tid, c in self.containers.items():
            if tag_id is None or tid == tag_id:
                self.set_pose(tid, c['x'], c['y'], 0.0, c['yaw'])
        self.say('reset')

    # ---- 10 Hz while attached: carry the container above the robot
    def follow(self):
        if self.attached is None or self.pending:
            return
        pose = self.robot_pose()
        if pose is None:
            return
        fut = self.set_pose(self.attached, pose[0], pose[1], self.carry_z, pose[2])
        if fut:
            self.pending = True
            fut.add_done_callback(lambda _: setattr(self, 'pending', False))


def main():
    rclpy.init()
    rclpy.spin(Magnet())


if __name__ == '__main__':
    main()
