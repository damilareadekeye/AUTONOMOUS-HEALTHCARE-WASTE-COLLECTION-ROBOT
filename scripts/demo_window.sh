#!/bin/bash
# Re-open the Gazebo window with a clean demo layout: only the 3D view, no side panels (for the demo video).
# The simulation keeps running; only the window (client) is restarted.   Usage: bash scripts/demo_window.sh
HERE="$(dirname "$(readlink -f "$0")")"
source "$HERE/env.sh"
for p in $(pgrep -f "gz sim.*-g"); do [ "$p" != "$$" ] && kill "$p" 2>/dev/null; done
sleep 2
setsid nohup gz sim -g --gui-config "$HERE/demo_gui.config" > /tmp/gz_gui.log 2>&1 < /dev/null &
sleep 8
tail -3 /tmp/gz_gui.log
