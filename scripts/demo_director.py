#!/usr/bin/env python3
"""Camera director for the demo video: moves the Gazebo camera to a good view for each task stage.

    python3 scripts/demo_director.py            # runs until Ctrl-C (or 600 s)

Reads the status file written by demo_status_feed.py and calls demo_camera.sh when the stage changes.
"""
import json
import os
import subprocess
import sys
import time

STATUS = '/mnt/c/Users/Aorus15/AppData/Local/Temp/hcw_status.json'
HERE = os.path.dirname(os.path.abspath(__file__))
# stage -> camera arguments for demo_camera.sh (x y height, looking straight down)
VIEWS = {
    'IDLE': ('top', '24', '-22', '48'),
    'NAVIGATE_TO_POINT': ('top', '12', '-26', '17'),
    'VERIFY': ('top', '13', '-23', '10'),
    'ATTACH': ('top', '13', '-23', '10'),
    'NAVIGATE_TO_STORAGE': ('top', '22', '-20', '40'),
    'RELEASE': ('top', '31', '-12', '13'),
    'REPORT': ('top', '31', '-12', '13'),
    'RETURN_HOME': ('top', '22', '-22', '42'),
    'FAILED': ('top', '12', '-23', '14'),
}


def main():
    last = None
    t0 = time.time()
    while time.time() - t0 < 600:
        try:
            with open(STATUS) as f:
                d = json.load(f)
        except (OSError, ValueError):
            time.sleep(0.3)
            continue
        state, point = d.get('state', 'IDLE'), d.get('point', '')
        key = (state, point)
        if key != last and state in VIEWS:
            args = list(VIEWS[state])
            if state in ('VERIFY', 'ATTACH', 'FAILED'):   # close-up on the room of the current task
                args[2] = {'A': '-20', 'B': '-26', 'C': '-32'}.get(point, args[2])
            subprocess.run(['bash', os.path.join(HERE, 'demo_camera.sh')] + args, capture_output=True, timeout=20)
            print(time.strftime('%H:%M:%S'), state, point, args, flush=True)
            last = key
        time.sleep(0.4)


if __name__ == '__main__':
    main()
