#!/bin/bash
# Show whether any simulation process is still running (prints a count and the first few).
n=$(pgrep -fc "gz sim|nav2_|task_manager|ign gazebo|ros_gz")
echo "simulation processes: $n"
pgrep -fa "gz sim|nav2_|task_manager|ros_gz" | cut -c1-70 | head -5
