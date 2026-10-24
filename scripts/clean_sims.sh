#!/usr/bin/env bash
# Stop every running simulation, RViz and ROS launch. Run before starting a new simulation.
# Patterns are specific on purpose so this script never kills the terminal that called it.
pkill -f "gz sim"
pkill -f "bin/ros2 launch"
pkill -f "lib/rviz2/rviz2"
pkill -f "ros_gz_bridge/parameter_bridge"
pkill -f "ros_gz_image/image_bridge"
exit 0
