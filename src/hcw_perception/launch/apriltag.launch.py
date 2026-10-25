"""AprilTag detection on the TurtleBot's camera.

    ros2 launch hcw_perception apriltag.launch.py

Publishes /detections (apriltag_msgs/AprilTagDetectionArray) and a TF frame per tag
(tag_A, tag_B, tag_C, tag_wrong) and starts the verifier node (/perception/target_status).
It only observes: it never publishes motor commands.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    config = os.path.join(get_package_share_directory('hcw_perception'), 'config', 'apriltag.yaml')
    apriltag = Node(
        package='apriltag_ros', executable='apriltag_node', name='apriltag', output='screen',
        parameters=[config, {'use_sim_time': True}],
        remappings=[('image_rect', '/rgbd_camera/image'),
                    ('camera_info', '/rgbd_camera/camera_info')])
    verifier = Node(package='hcw_perception', executable='verifier', name='verifier', output='screen',
                    parameters=[{'use_sim_time': True}])
    return LaunchDescription([apriltag, verifier])
