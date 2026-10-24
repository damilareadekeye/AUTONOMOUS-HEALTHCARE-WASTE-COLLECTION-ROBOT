source /home/damilare/hcw_ws/scripts/env.sh
cd /home/damilare/hcw_ws
say() { echo "[$(date +%H:%M:%S)] $*"; }

rtf() { gz topic -e -t /stats -n 1 2>/dev/null | grep real_time_factor | awk '{printf "%.2f", $2}'; }

say "starting simulation"
setsid nohup ros2 launch hcw_bringup sim_clinic.launch.py > /tmp/hcw_launch.log 2>&1 &
n=0; until timeout 8 ros2 topic echo /odom --once >/dev/null 2>&1; do sleep 3; n=$((n+1)); [ $n -gt 60 ] && { say "FAIL: robot never appeared"; exit 1; }; done
sleep 20
say "simulation up, real-time factor $(rtf)"

start_nav() {
  setsid nohup ros2 launch hcw_navigation navigation.launch.py > /tmp/hcw_nav.log 2>&1 &
  for i in $(seq 1 40); do
    timeout 8 ros2 topic echo /amcl_pose --once >/dev/null 2>&1 && return 0
    sleep 3
  done
  return 1
}
for attempt in 1 2 3; do
  say "starting Nav2 (attempt $attempt)"
  if start_nav; then say "Nav2 localised"; break; fi
  say "Nav2 did not come up; restarting it"
  pkill -f "bin/ros2 launch hcw_navigation"; pkill -f nav2_; pkill -f lifecycle_manager; sleep 5
  [ $attempt -eq 3 ] && { say "FAIL: Nav2 never started"; exit 1; }
done
setsid nohup ros2 launch hcw_perception apriltag.launch.py > /tmp/hcw_tags.log 2>&1 &
sleep 10
say "real-time factor $(rtf)"

ids() { ros2 run hcw_perception tag_monitor --collect 6 2>/dev/null | tail -1; }
for P in collection_A collection_B collection_C storage home; do
  say "going to $P"
  timeout 420 ros2 run hcw_navigation go_to $P 2>&1 | grep -E "reached|FAILED" || echo "$P TIMED OUT"
  case $P in collection_*) sleep 2; echo "  tags seen at $P: $(ids)";; esac
  echo "  amcl pose: $(timeout 6 ros2 topic echo /amcl_pose --once --field pose.pose.position 2>/dev/null | grep -E '^[xy]:' | tr '\n' ' ')"
done
say "real-time factor $(rtf)"
echo ALL-DONE
