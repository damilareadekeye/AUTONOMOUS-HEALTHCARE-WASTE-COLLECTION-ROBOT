#!/usr/bin/env python3
"""Generate the hazard-warning models of the storage area: a floor decal and a wall sign.

    python3 src/hcw_world/scripts/make_hazard_textures.py

Writes src/hcw_world/models/hcw_hazard_floor/ and hcw_hazard_sign/ (SDF + PNG texture). The symbols are an abstract
biohazard-style trefoil and a warning triangle, drawn here with OpenCV (not an official standard symbol). Visual only.
"""
import math
import os

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.normpath(os.path.join(HERE, '..', 'models'))

AMBER = (60, 190, 255)      # BGR: warm amber/yellow
YELLOW = (0, 215, 255)
BLACK = (20, 20, 20)
RED = (30, 30, 200)

FLOOR_SIZE_M = (7.2, 1.7)   # world size of the floor decal (x, y)
SIGN_SIZE_M = (0.9, 0.6)    # world size of one wall sign

SDF = """<?xml version="1.0"?>
<sdf version="1.9">
  <model name="{name}">
    <static>true</static>
    <link name="l">
      <visual name="v">
        <pose>0 0 0 0 0 {roll_yaw}</pose>
        <geometry><plane><normal>{normal}</normal><size>{sx} {sy}</size></plane></geometry>
        <material>
          <ambient>1 1 1 1</ambient>
          <diffuse>1 1 1 1</diffuse>
          <pbr><metal><albedo_map>model://{name}/materials/textures/{png}</albedo_map></metal></pbr>
        </material>
      </visual>
    </link>
  </model>
</sdf>
"""

CONFIG = """<?xml version="1.0"?>
<model>
  <name>{name}</name>
  <version>1.0</version>
  <sdf version="1.9">model.sdf</sdf>
  <description>{desc}</description>
</model>
"""


def trefoil(img, cx, cy, r):
    """Abstract biohazard-style symbol: three overlapping rings around a small centre ring."""
    for k in range(3):
        a = math.radians(90 + 120 * k)
        x, y = int(cx + 0.55 * r * math.cos(a)), int(cy - 0.55 * r * math.sin(a))
        cv2.circle(img, (x, y), int(0.62 * r), BLACK, max(2, int(0.16 * r)), cv2.LINE_AA)
    cv2.circle(img, (int(cx), int(cy)), int(0.20 * r), BLACK, -1, cv2.LINE_AA)
    cv2.circle(img, (int(cx), int(cy)), int(0.09 * r), AMBER, -1, cv2.LINE_AA)


def warning_triangle(img, cx, cy, r):
    pts = np.array([[cx, cy - r], [cx - r * 0.87, cy + r * 0.5], [cx + r * 0.87, cy + r * 0.5]], np.int32)
    cv2.fillPoly(img, [pts], BLACK, cv2.LINE_AA)
    inner = np.array([[cx, cy - r * 0.72], [cx - r * 0.62, cy + r * 0.38], [cx + r * 0.62, cy + r * 0.38]], np.int32)
    cv2.fillPoly(img, [inner], YELLOW, cv2.LINE_AA)
    cv2.rectangle(img, (int(cx - r * 0.06), int(cy - r * 0.38)), (int(cx + r * 0.06), int(cy + r * 0.10)), BLACK, -1)
    cv2.circle(img, (int(cx), int(cy + r * 0.26)), int(r * 0.07), BLACK, -1, cv2.LINE_AA)


def stripes_border(img, band):
    """Black/yellow diagonal stripes in a band of `band` px around the edge."""
    h, w = img.shape[:2]
    layer = np.full_like(img, YELLOW)
    step = int(band * 1.1)
    for k in range(-h, w + h, step):
        cv2.line(layer, (k, 0), (k + h, h), BLACK, int(step / 2))
    mask = np.zeros((h, w), np.uint8)
    mask[:band, :] = 255
    mask[-band:, :] = 255
    mask[:, :band] = 255
    mask[:, -band:] = 255
    img[mask > 0] = layer[mask > 0]


def floor_texture():
    ppm = 200                                                # pixels per metre
    w, h = int(FLOOR_SIZE_M[0] * ppm), int(FLOOR_SIZE_M[1] * ppm)
    img = np.full((h, w, 3), AMBER, np.uint8)
    stripes_border(img, 46)
    cy = h // 2
    for i, frac in enumerate((0.14, 0.36, 0.64, 0.86)):      # symbols spread along the decal
        (trefoil if i % 2 == 0 else warning_triangle)(img, int(w * frac), cy, 90)
    cv2.line(img, (int(w * 0.25), cy), (int(w * 0.25), cy), BLACK, 1)
    return img


def sign_texture():
    ppm = 667                                                # 600 x 400 px for 0.9 x 0.6 m
    w, h = 600, 400
    img = np.full((h, w, 3), YELLOW, np.uint8)
    cv2.rectangle(img, (6, 6), (w - 7, h - 7), BLACK, 12)
    trefoil(img, 120, h // 2, 85)
    cv2.putText(img, 'HAZARDOUS', (225, 130), cv2.FONT_HERSHEY_DUPLEX, 1.55, BLACK, 4, cv2.LINE_AA)
    cv2.putText(img, 'WASTE', (225, 215), cv2.FONT_HERSHEY_DUPLEX, 1.9, RED, 5, cv2.LINE_AA)
    cv2.putText(img, 'AUTHORISED ACCESS', (200, 300), cv2.FONT_HERSHEY_DUPLEX, 0.85, BLACK, 2, cv2.LINE_AA)
    cv2.putText(img, 'ONLY', (200, 345), cv2.FONT_HERSHEY_DUPLEX, 0.85, BLACK, 2, cv2.LINE_AA)
    return img


def write_model(name, png, img, size, normal, desc):
    d = os.path.join(MODELS, name)
    os.makedirs(os.path.join(d, 'materials', 'textures'), exist_ok=True)
    cv2.imwrite(os.path.join(d, 'materials', 'textures', png), img)
    with open(os.path.join(d, 'model.sdf'), 'w') as f:
        f.write(SDF.format(name=name, png=png, sx=size[0], sy=size[1], normal=normal, roll_yaw=0))
    with open(os.path.join(d, 'model.config'), 'w') as f:
        f.write(CONFIG.format(name=name, desc=desc))
    print('wrote', d)


def main():
    write_model('hcw_hazard_floor', 'floor.png', floor_texture(), FLOOR_SIZE_M, '0 0 1',
                'Hazard-striped floor decal for the waste storage area.')
    write_model('hcw_hazard_sign', 'sign.png', sign_texture(), SIGN_SIZE_M, '0 -1 0',
                'Wall sign: hazardous waste, authorised access only (faces south).')


if __name__ == '__main__':
    main()
