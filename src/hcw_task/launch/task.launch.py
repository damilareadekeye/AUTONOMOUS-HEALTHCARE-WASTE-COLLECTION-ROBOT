"""Task manager + simulated magnet (+ the Gazebo set_pose bridge the magnet needs).

    ros2 launch hcw_task task.launch.py
    ros2 launch hcw_task task.launch.py wrong_container:=true obstacle:=false notes:="test 7"   # labels for the CSV
    ros2 param set /task_manager reset_container false    # for a missing or wrong container test (see docs/07)

Needs: simulation, navigation.launch.py and apriltag.launch.py already running.
Then:  ros2 run hcw_task request A
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    bridge = Node(
        package='ros_gz_bridge', executable='parameter_bridge', name='bridge_set_pose', output='screen',
        arguments=['/world/sim_world/set_pose@ros_gz_interfaces/srv/SetEntityPose'])
    magnet = Node(package='hcw_task', executable='magnet', name='magnet', output='screen',
                  parameters=[{'use_sim_time': True}])
    manager = Node(
        package='hcw_task', executable='task_manager', name='task_manager', output='screen',
        parameters=[{'use_sim_time': True,
                     # ParameterValue(..., str): otherwise "no" and "yes" are read as booleans
                     'wrong_container': ParameterValue(LaunchConfiguration('wrong_container'), value_type=bool),
                     'obstacle': ParameterValue(LaunchConfiguration('obstacle'), value_type=bool),
                     'notes': ParameterValue(LaunchConfiguration('notes'), value_type=str)}])
    return LaunchDescription([
        DeclareLaunchArgument('wrong_container', default_value='false'),
        DeclareLaunchArgument('obstacle', default_value='false'),
        DeclareLaunchArgument('notes', default_value=''),
        bridge, magnet, manager])
