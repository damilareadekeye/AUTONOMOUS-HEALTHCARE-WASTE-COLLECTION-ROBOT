#!/usr/bin/env bash
# Run repeated tasks for the Week 4 results, with no AI and no supervision needed.
#   scripts/start_stack.sh                       # first: starts everything and waits until ready
#   scripts/run_batch.sh 18                      # 18 normal tasks, round robin A, B, C
#   scripts/run_batch.sh 18 --with-failures      # plus 6 fault cases: missing and wrong container at A, B and C
# Each task takes about 3.5 minutes (simulated = real time). 18 normal + 6 fault cases is about 1.5 hours.
# Results go to ~/hcw_ws/results/runs.csv; a summary is printed at the end (scripts/summarize_runs.py).
source "$HOME/hcw_ws/scripts/env.sh"
source "$HOME/hcw_ws/install/setup.bash"
N=${1:-3}; FAILURES=0; [ "$2" = "--with-failures" ] && FAILURES=1
say() { echo "[$(date +%H:%M:%S)] $*"; }
CSV=$HOME/hcw_ws/results/runs.csv
FIRST=$(( $( [ -f "$CSV" ] && tail -n +2 "$CSV" | cut -d, -f1 | sort -n | tail -1 || echo 0) + 1 ))

ros2 topic info /hcw/task_request 2>/dev/null | grep -q "Subscription count: [1-9]" || { say "the task manager is not running: run scripts/start_stack.sh first"; exit 1; }

# container home poses from locations.yaml:  "<tag> <x> <y> <yaw>"
poses() { python3 - <<'PY'
import yaml, os
from ament_index_python.packages import get_package_share_directory
c = yaml.safe_load(open(os.path.join(get_package_share_directory('hcw_world'), 'config', 'locations.yaml')))['containers']
for k in c:
    if k.get('enabled', True): print(k['tag_id'], k['x'], k['y'], k['yaw'])
PY
}
move() {   # move <tag> <x> <y> <yaw>
  python3 - "$@" <<'PY'
import math, subprocess, sys
tag, x, y, yaw = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
req = ("{entity: {name: 'hcw_container_%s', type: 2}, pose: {position: {x: %s, y: %s, z: 0.0}, "
       "orientation: {x: 0.0, y: 0.0, z: %f, w: %f}}}" % (tag, x, y, math.sin(yaw / 2), math.cos(yaw / 2)))
subprocess.run(['ros2', 'service', 'call', '/world/sim_world/set_pose',
                'ros_gz_interfaces/srv/SetEntityPose', req], capture_output=True)
PY
}
reset_all() { ros2 topic pub --once /magnet/command std_msgs/msg/String "{data: 'reset:all'}" >/dev/null 2>&1; sleep 2; }
task() { timeout 900 ros2 run hcw_task request "$1" 2>&1 | grep -E "COMPLETED|FAILED|REJECTED" | tail -1; }
note() { ros2 param set /task_manager notes "$1" >/dev/null 2>&1; }   # no colon in the text: the CLI would read it as YAML

POINTS=(A B C)
say "batch: $N normal tasks$([ $FAILURES = 1 ] && echo ' + 6 fault cases'), first run id $FIRST"
reset_all; ros2 param set /task_manager reset_container true >/dev/null 2>&1
for i in $(seq 1 "$N"); do
  p=${POINTS[$(( (i-1) % 3 ))]}
  note "batch normal $i"
  say "normal task $i of $N at $p"
  say "  -> $(task $p)"
done

if [ "$FAILURES" = 1 ]; then
  declare -A TAG=( [A]=11 [B]=12 [C]=13 )
  declare -A OTHER=( [A]=12 [B]=13 [C]=11 )
  ros2 param set /task_manager reset_container false >/dev/null 2>&1
  for p in A B C; do
    t=${TAG[$p]}; o=${OTHER[$p]}
    home_of() { poses | awk -v t="$1" '$1==t {print $2, $3, $4}'; }
    # missing container: the container is moved far outside the building
    reset_all; move "$t" 5.0 -45.0 0.0
    note "batch fault missing container at $p"
    say "fault: missing container at $p"; say "  -> $(task $p)"
    # wrong container: another container stands in its place
    reset_all; read hx hy hyaw <<< "$(home_of "$t")"
    move "$t" 5.0 -45.0 0.0; move "$o" "$hx" "$hy" "$hyaw"
    ros2 param set /task_manager wrong_container true >/dev/null 2>&1
    note "batch fault wrong container at $p"
    say "fault: wrong container at $p"; say "  -> $(task $p)"
    ros2 param set /task_manager wrong_container false >/dev/null 2>&1
  done
  reset_all; ros2 param set /task_manager reset_container true >/dev/null 2>&1
fi
note ""
say "batch finished. Summary of this batch:"
python3 "$HOME/hcw_ws/scripts/summarize_runs.py" --from-run "$FIRST"
