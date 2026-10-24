"""Clinic world + TurtleBot 4 in Gazebo Harmonic, with RViz.

    ros2 launch hcw_bringup sim_clinic.launch.py
    ros2 launch hcw_bringup sim_clinic.launch.py profile:=building   # fastest, empty shell
    ros2 launch hcw_bringup sim_clinic.launch.py headless:=True      # no windows
    ros2 launch hcw_bringup sim_clinic.launch.py x_pose:=30.9 y_pose:=-17.3

Navigation (Nav2) is not started here; this is the simulation layer only.
We do not reuse nav2_minimal_tb4_sim/simulation.launch.py: it converts the world with xacro
while Gazebo is already starting, and our large clinic world loses that race.
"""
import os
import tempfile

from ament_index_python.packages import get_package_share_directory
from hcw_world.world_builder import build_world, PROFILES, resource_paths
from launch import LaunchDescription
from launch.actions import (AppendEnvironmentVariable, DeclareLaunchArgument,
                            IncludeLaunchDescription, OpaqueFunction, TimerAction)
from launch.conditions import UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


def _start_simulation(context):
    tb4_sim = get_package_share_directory('nav2_minimal_tb4_sim')
    tb4_desc = get_package_share_directory('nav2_minimal_tb4_description')
    ros_gz_sim = get_package_share_directory('ros_gz_sim')
    robot_xacro = os.path.join(tb4_desc, 'urdf', 'standard', 'turtlebot4.urdf.xacro')
    headless = LaunchConfiguration('headless')

    profile = LaunchConfiguration('profile').perform(context)
    world_sdf = build_world(os.path.join(tempfile.gettempdir(), 'hcw_clinic.sdf'), profile)

    gz_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': '-r -s ' + world_sdf}.items())

    gz_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        condition=UnlessCondition(headless),
        launch_arguments={'gz_args': '-v4 -g'}.items())

    robot_state_publisher = Node(
        package='robot_state_publisher', executable='robot_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True,
                     'robot_description': Command(['xacro ', robot_xacro])}])

    # Bridges (cmd_vel, odom, scan, imu, camera...) and spawning of the robot.
    spawn_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(tb4_sim, 'launch', 'spawn_tb4.launch.py')),
        launch_arguments={
            'robot_name': 'turtlebot4',
            'x_pose': LaunchConfiguration('x_pose'),
            'y_pose': LaunchConfiguration('y_pose'),
            'yaw': LaunchConfiguration('yaw'),
        }.items())

    rviz = Node(
        condition=UnlessCondition(headless),
        package='rviz2', executable='rviz2', output='screen',
        arguments=['-d', os.path.join(tb4_desc, 'rviz', 'config.rviz')],
        parameters=[{'use_sim_time': True}])

    # The window must start after the server is up, otherwise it can exit silently.
    return [gz_server, TimerAction(period=8.0, actions=[gz_client]),
            robot_state_publisher, spawn_robot, rviz]


def generate_launch_description():
    args = [
        DeclareLaunchArgument('headless', default_value='False',
                              description='True = no Gazebo window and no RViz'),
        DeclareLaunchArgument('profile', default_value='building',
                              description='How much of the clinic to load: %s' % (PROFILES,)),
        # Default: parking spot "L1_sub_waiting_area_1" on the clinic ground floor.
        DeclareLaunchArgument('x_pose', default_value='8.0'),
        DeclareLaunchArgument('y_pose', default_value='-31.7'),
        DeclareLaunchArgument('yaw', default_value='0.0'),
    ]
    env = [AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', p) for p in resource_paths()]
    return LaunchDescription(args + env + [OpaqueFunction(function=_start_simulation)])
