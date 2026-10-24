"""Nav2 on the saved clinic map (AMCL localisation). The map frame equals the world frame.

    ros2 launch hcw_navigation navigation.launch.py
    ros2 launch hcw_navigation navigation.launch.py rviz:=True

Start the simulation first: ros2 launch hcw_bringup sim_clinic.launch.py
The robot is assumed to start at the home spot (8.0, -31.7); see amcl.initial_pose in config/nav2_params.yaml.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav2 = get_package_share_directory('nav2_bringup')
    hcw = get_package_share_directory('hcw_navigation')

    bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'slam': 'False',
            'map': os.path.join(hcw, 'maps', 'clinic.yaml'),
            'use_sim_time': 'true',
            'params_file': os.path.join(hcw, 'config', 'nav2_params.yaml'),
            'autostart': 'true',
            'use_composition': 'False',
        }.items())

    rviz = Node(
        condition=IfCondition(LaunchConfiguration('rviz')),
        package='rviz2', executable='rviz2', output='screen',
        arguments=['-d', os.path.join(nav2, 'rviz', 'nav2_default_view.rviz')],
        parameters=[{'use_sim_time': True}])

    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='False', description='True = also open RViz'),
        bringup, rviz])
