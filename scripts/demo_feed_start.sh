#!/bin/bash
# Start the status feed for the demo panel (background). Needs the stack running.
source "$(dirname "$0")/env.sh"
pkill -f demo_status_feed.py 2>/dev/null
setsid nohup python3 "$(dirname "$0")/demo_status_feed.py" > /tmp/feed.log 2>&1 < /dev/null &
sleep 4
cat /tmp/feed.log; ls -la /mnt/c/Users/Aorus15/AppData/Local/Temp/hcw_status.json
