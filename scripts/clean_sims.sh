#!/usr/bin/env bash
# Stop every running simulation, Nav2, perception, RViz and ROS launch, including leftover child
# processes (duplicate Nav2 nodes from an earlier run make a new Nav2 fail to start).
# Run before starting a new simulation. Patterns are specific on purpose so this script never
# kills the terminal that called it.
pkill -f "bin/ros2 launch"
pkill -f "bin/ros2 run"
pkill -f "gz sim"
pkill -f "lib/rviz2/rviz2"
pkill -f "ros_gz_bridge/parameter_bridge"
pkill -f "ros_gz_image/image_bridge"
pkill -f "lib/nav2_"
pkill -f "lib/slam_toolbox"
pkill -f "lib/apriltag_ros"
pkill -f "lib/robot_state_publisher"
pkill -f "lib/rclcpp_components"
pkill -f "lib/hcw_task"            # task manager and magnet: a second copy answers the same requests
pkill -f "lib/hcw_perception"      # verifier
pkill -f "bridge_set_pose"
sleep 2
pkill -9 -f "lib/nav2_"
pkill -9 -f "gz sim"
ros2 daemon stop >/dev/null 2>&1
exit 0
