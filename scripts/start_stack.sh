#!/usr/bin/env bash
# Start the whole system in the background: simulation, Nav2, tag detection, task manager.
#   scripts/start_stack.sh            # no Gazebo window (fast, use for tests and batches)
#   scripts/start_stack.sh gui        # with the Gazebo window (slower, good for showing the demo)
# Prints a timestamped line per stage and "STACK READY" at the end (about 1.5 minutes).
# Logs: /tmp/hcw_launch.log /tmp/hcw_nav.log /tmp/hcw_tags.log /tmp/hcw_task.log
# Stop everything with: scripts/clean_sims.sh
source "$HOME/hcw_ws/scripts/env.sh"
cd "$HOME/hcw_ws" || exit 1
say() { echo "[$(date +%H:%M:%S)] $*"; }

bash "/home/damilare/hcw_ws/scripts/clean_sims.sh"
sleep 3
GUI=False; [ "$1" = "gui" ] && GUI=True

say "building packages"
colcon build --symlink-install 2>&1 | tail -1
source "$HOME/hcw_ws/install/setup.bash"

say "starting simulation (gui:=$GUI)"
setsid nohup ros2 launch hcw_bringup sim_clinic.launch.py gui:=$GUI > /tmp/hcw_launch.log 2>&1 &
n=0; until timeout 8 ros2 topic echo /odom --once >/dev/null 2>&1; do
  sleep 3; n=$((n+1)); [ $n -gt 60 ] && { say "FAILED: the robot never appeared (see /tmp/hcw_launch.log)"; exit 1; }
done
sleep 15

say "starting Nav2"
setsid nohup ros2 launch hcw_navigation navigation.launch.py > /tmp/hcw_nav.log 2>&1 &
n=0; until timeout 8 ros2 topic echo /amcl_pose --once >/dev/null 2>&1; do
  sleep 3; n=$((n+1)); [ $n -gt 40 ] && { say "FAILED: Nav2 did not localise (see /tmp/hcw_nav.log). Run scripts/clean_sims.sh and try again"; exit 1; }
done
say "Nav2 localised"

say "starting tag detection and the task manager"
setsid nohup ros2 launch hcw_perception apriltag.launch.py > /tmp/hcw_tags.log 2>&1 &
setsid nohup ros2 launch hcw_task task.launch.py > /tmp/hcw_task.log 2>&1 &
n=0; until ros2 topic info /hcw/task_request 2>/dev/null | grep -q "Subscription count: [1-9]"; do
  sleep 3; n=$((n+1)); [ $n -gt 30 ] && { say "FAILED: task manager did not start (see /tmp/hcw_task.log)"; exit 1; }
done
say "STACK READY. Ask for a task:  ros2 run hcw_task request A"
