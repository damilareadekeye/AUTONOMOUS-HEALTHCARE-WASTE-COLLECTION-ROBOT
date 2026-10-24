#!/usr/bin/env python3
"""Mark every consulting-room doorway as blocked on the saved map.

    python3 src/hcw_navigation/scripts/seal_room_doors.py

Why: the clinic's door models are removed from the simulation (they would stay shut), so every
consulting room is open. The room interiors are not mapped, and Nav2 planned shortcuts into them
and then could not plan from inside. The robot only has to stop in the corridor in front of a door
(the camera sees the container through the open door), so the doorways are blocked on the MAP only.

Run it once after saving a new map. It is safe to run again (it only draws filled circles).
The door positions come from the Open-RMF clinic world (inline models L1_*_consult_rm_*_outer).
"""
import os
import re
import sys

import cv2

RADIUS_M = 0.55            # blocked disc around each door centre
MAPS = os.path.join(os.path.dirname(__file__), '..', 'maps')
WORLD = os.path.expanduser(
    '~/eval/rmf_ws/install/rmf_demos_maps/share/rmf_demos_maps/maps/clinic/clinic.world')


def door_centres():
    text = open(os.path.realpath(WORLD), encoding='utf-8').read()
    pat = re.compile(r'<model name="(L1_\w*consult_rm_\d+_outer)">\s*<pose>\s*(\S+)\s+(\S+)')
    return [(m.group(1), float(m.group(2)), float(m.group(3))) for m in pat.finditer(text)]


def main():
    yaml_path = os.path.join(MAPS, 'clinic.yaml')
    res, origin = None, None
    for line in open(yaml_path):
        if line.startswith('resolution:'):
            res = float(line.split(':')[1])
        if line.startswith('origin:'):
            origin = [float(v) for v in re.findall(r'-?\d+\.?\d*', line.split(':', 1)[1])]
    pgm_path = os.path.join(MAPS, 'clinic.pgm')
    img = cv2.imread(pgm_path, cv2.IMREAD_GRAYSCALE)
    height = img.shape[0]
    doors = door_centres()
    for name, x, y in doors:
        px = int(round((x - origin[0]) / res))
        py = height - 1 - int(round((y - origin[1]) / res))
        cv2.circle(img, (px, py), int(round(RADIUS_M / res)), 0, thickness=-1)
    cv2.imwrite(pgm_path, img)
    print('sealed %d consulting-room doorways in %s' % (len(doors), pgm_path))
    return 0 if doors else 1


if __name__ == '__main__':
    sys.exit(main())
