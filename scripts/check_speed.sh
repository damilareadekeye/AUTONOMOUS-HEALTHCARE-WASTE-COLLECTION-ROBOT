#!/usr/bin/env bash
# Check how fast the simulation runs (percent of real time). Run it before a demo, with the stack running.
#   bash scripts/check_speed.sh
# 70 % or more: good. 40 to 70 %: works, tasks take longer; close other programs and plug the laptop in.
# Below 40 %: restart (scripts/clean_sims.sh then scripts/start_stack.sh gui) and close everything else.
source "$HOME/hcw_ws/scripts/env.sh" >/dev/null 2>&1
get() { gz topic -e -t /stats -n 1 2>/dev/null | tr -d '\n' | sed -E 's/.*sim_time \{ *sec: ([0-9]+).*real_time \{ *sec: ([0-9]+).*/\1 \2/'; }
a=$(get)
[ -z "$a" ] && { echo "The simulation is not running. Start it with: bash scripts/start_stack.sh gui"; exit 1; }
sleep 20
b=$(get)
set -- $a $b
speed=$(( ($3-$1)*100/($4-$2) ))
echo "Simulation speed over 20 s: $speed % of real time"
if [ "$speed" -ge 70 ]; then echo "Good for a demo."
elif [ "$speed" -ge 40 ]; then echo "Works, but a task takes about $((400/speed)) minutes instead of 4. Close other programs, plug in the laptop."
else echo "Too slow. Run scripts/clean_sims.sh, close other programs, start again."; fi
