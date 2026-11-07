#!/usr/bin/env bash
# Stage a failure for a demo, then ask for the task yourself. The stack must be running.
#   bash scripts/demo_fault.sh missing A     # container 11 removed from point A: the task will FAIL (no tag seen)
#   bash scripts/demo_fault.sh wrong A       # the container of point B stands at A: the task will FAIL (wrong tag)
#   bash scripts/demo_fault.sh reset         # put every container back and return to normal
# Then:  ros2 run hcw_task request A       (it takes about 2 to 3 minutes to fail and drive home)
source "$HOME/hcw_ws/scripts/env.sh" >/dev/null 2>&1
source "$HOME/hcw_ws/install/setup.bash"
mode=$1; point=${2:-A}
declare -A TAG=( [A]=11 [B]=12 [C]=13 )
declare -A OTHER=( [A]=12 [B]=13 [C]=11 )
move() {   # move <tag> <x> <y> <yaw>
  python3 - "$@" <<'PY'
import math, subprocess, sys
tag, x, y, yaw = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
req = ("{entity: {name: 'hcw_container_%s', type: 2}, pose: {position: {x: %s, y: %s, z: 0.0}, "
       "orientation: {x: 0.0, y: 0.0, z: %f, w: %f}}}" % (tag, x, y, math.sin(yaw / 2), math.cos(yaw / 2)))
subprocess.run(['ros2', 'service', 'call', '/world/sim_world/set_pose', 'ros_gz_interfaces/srv/SetEntityPose', req], capture_output=True)
PY
}
home_pose() {   # home_pose <tag>  ->  "x y yaw" from locations.yaml
  python3 - "$1" <<'PY'
import os, sys, yaml
from ament_index_python.packages import get_package_share_directory
c = yaml.safe_load(open(os.path.join(get_package_share_directory('hcw_world'), 'config', 'locations.yaml')))['containers']
for k in c:
    if str(k['tag_id']) == sys.argv[1]: print(k['x'], k['y'], k['yaw'])
PY
}
reset_all() { ros2 topic pub --once /magnet/command std_msgs/msg/String "{data: 'reset:all'}" >/dev/null 2>&1; sleep 2; }

case "$mode" in
  missing)
    [ -z "${TAG[$point]}" ] && { echo "point must be A, B or C"; exit 2; }
    reset_all
    ros2 param set /task_manager reset_container false >/dev/null 2>&1
    move "${TAG[$point]}" 5.0 -45.0 0.0
    echo "Container ${TAG[$point]} removed from point $point. Now run:  ros2 run hcw_task request $point" ;;
  wrong)
    [ -z "${TAG[$point]}" ] && { echo "point must be A, B or C"; exit 2; }
    reset_all
    ros2 param set /task_manager reset_container false >/dev/null 2>&1
    read hx hy hyaw <<< "$(home_pose "${TAG[$point]}")"
    move "${TAG[$point]}" 5.0 -45.0 0.0
    move "${OTHER[$point]}" "$hx" "$hy" "$hyaw"
    ros2 param set /task_manager wrong_container true >/dev/null 2>&1
    echo "The container with tag ${OTHER[$point]} now stands at point $point. Now run:  ros2 run hcw_task request $point" ;;
  reset)
    ros2 param set /task_manager reset_container true >/dev/null 2>&1
    ros2 param set /task_manager wrong_container false >/dev/null 2>&1
    reset_all
    echo "All containers are back in their places." ;;
  *) echo "usage: bash scripts/demo_fault.sh missing|wrong A|B|C   or   bash scripts/demo_fault.sh reset"; exit 2 ;;
esac
