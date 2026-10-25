#!/usr/bin/env python3
"""Generate the Gazebo container models (a coloured bin with an AprilTag on its +X face).

    python3 src/hcw_world/scripts/make_tag_models.py

Writes src/hcw_world/models/hcw_container_<id>/ for each tag id. Run it again after changing
the constants below. Tag family: tag36h11 (matches apriltag_ros cfg/tags_36h11.yaml).
Tag ids: 11 = collection point A, 12 = B, 13 = C, 14 = a wrong container (test only).
"""
import os

import cv2
import numpy as np

TAG_IDS = [11, 12, 13, 14]
TAG_SIZE = 0.30          # m, black square side (the white border is extra)
BIN = (0.40, 0.40, 0.60)  # m: x, y, z of the container
TAG_CENTER_Z = 0.30      # m above the floor (the TurtleBot camera is at about this height)

# Per-tag bin colour (R, G, B), 0-1 range. Keeps A, B, C visibly distinct and makes the
# wrong container (14) clearly different from all three correct ones.
COLORS = {
    11: (0.10, 0.30, 0.90),   # collection A - blue
    12: (0.10, 0.70, 0.20),   # collection B - green
    13: (0.90, 0.55, 0.10),   # collection C - orange
    14: (0.85, 0.10, 0.10),   # wrong container - red
}
DEFAULT_COLOR = (0.95, 0.80, 0.10)   # fallback (original yellow) for any id not listed above

SDF = """<?xml version="1.0"?>
<sdf version="1.9">
  <model name="hcw_container_{id}">
    <static>true</static>
    <link name="body">
      <collision name="collision">
        <pose>0 0 {hz} 0 0 0</pose>
        <geometry><box><size>{bx} {by} {bz}</size></box></geometry>
      </collision>
      <visual name="bin">
        <pose>0 0 {hz} 0 0 0</pose>
        <geometry><box><size>{bx} {by} {bz}</size></box></geometry>
        <material>
          <ambient>{cr} {cg} {cb} 1</ambient>
          <diffuse>{cr} {cg} {cb} 1</diffuse>
        </material>
      </visual>
      <visual name="tag{id}">
        <pose>{tx} 0 {tz} 0 0 0</pose>
        <geometry><plane><normal>1 0 0</normal><size>{ts} {ts}</size></plane></geometry>
        <material>
          <ambient>1 1 1 1</ambient>
          <diffuse>1 1 1 1</diffuse>
          <pbr><metal><albedo_map>model://hcw_container_{id}/materials/textures/tag{id}.png</albedo_map></metal></pbr>
        </material>
      </visual>
    </link>
  </model>
</sdf>
"""

CONFIG = """<?xml version="1.0"?>
<model>
  <name>hcw_container_{id}</name>
  <version>1.0</version>
  <sdf version="1.9">model.sdf</sdf>
  <description>Sealed-container stand-in with AprilTag tag36h11 id {id}.</description>
</model>
"""


def tag_image(tag_id, cells=10, px=40):
    """Tag with a white border, as a PNG-ready array (tag36h11 is 8x8 cells with a black ring)."""
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
    if hasattr(cv2.aruco, 'generateImageMarker'):             # OpenCV 4.7+
        marker = cv2.aruco.generateImageMarker(dictionary, tag_id, cells * px, borderBits=1)
    else:                                                     # OpenCV 4.6 (Ubuntu 24.04)
        marker = cv2.aruco.drawMarker(dictionary, tag_id, cells * px, borderBits=1)
    border = px                      # white quiet zone around the tag
    return cv2.copyMakeBorder(marker, border, border, border, border, cv2.BORDER_CONSTANT, value=255)


def main():
    root = os.path.join(os.path.dirname(__file__), '..', 'models')
    for tag_id in TAG_IDS:
        d = os.path.normpath(os.path.join(root, 'hcw_container_%d' % tag_id))
        os.makedirs(os.path.join(d, 'materials', 'textures'), exist_ok=True)
        img = tag_image(tag_id)
        cv2.imwrite(os.path.join(d, 'materials', 'textures', 'tag%d.png' % tag_id), img)
        total = TAG_SIZE * img.shape[0] / (img.shape[0] - 2 * 40)   # plane size incl. white border
        cr, cg, cb = COLORS.get(tag_id, DEFAULT_COLOR)
        with open(os.path.join(d, 'model.sdf'), 'w') as f:
            f.write(SDF.format(id=tag_id, bx=BIN[0], by=BIN[1], bz=BIN[2], hz=BIN[2] / 2,
                               tx=BIN[0] / 2 + 0.001, tz=TAG_CENTER_Z, ts=round(total, 4),
                               cr=cr, cg=cg, cb=cb))
        with open(os.path.join(d, 'model.config'), 'w') as f:
            f.write(CONFIG.format(id=tag_id))
        print('wrote', d)


if __name__ == '__main__':
    main()
