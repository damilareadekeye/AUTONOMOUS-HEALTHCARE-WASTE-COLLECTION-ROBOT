"""SLAM Toolbox (builds the map) + Nav2 (drives), on top of the running clinic simulation.

    ros2 launch hcw_navigation mapping.launch.py
    ros2 run hcw_navigation map_clinic          # drives the clinic corridors and saves the map

Start the simulation first: ros2 launch hcw_bringup sim_clinic.launch.py
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    slam = get_package_share_directory('slam_toolbox')
    nav2 = get_package_share_directory('nav2_bringup')
    hcw = get_package_share_directory('hcw_navigation')

    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(slam, 'launch', 'online_async_launch.py')),
        launch_arguments={
            'use_sim_time': 'true',
            'slam_params_file': os.path.join(hcw, 'config', 'slam_mapping.yaml'),
        }.items())

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2, 'launch', 'navigation_launch.py')),
        launch_arguments={
            'use_sim_time': 'true',
            'params_file': os.path.join(hcw, 'config', 'nav2_params.yaml'),
            'autostart': 'true',
        }.items())

    return LaunchDescription([slam_toolbox, navigation])
