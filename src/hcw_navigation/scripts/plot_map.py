#!/usr/bin/env python3
"""Draw the saved map with the named places and containers, for documents and approvals.

    python3 src/hcw_navigation/scripts/plot_map.py [output.png]    (default docs/images/clinic_map_locations.png)
"""
import os
import re
import sys

import cv2
import yaml

HERE = os.path.dirname(__file__)
MAPS = os.path.join(HERE, '..', 'maps')
LOCATIONS = os.path.join(HERE, '..', '..', 'hcw_world', 'config', 'locations.yaml')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', '..', 'docs', 'images', 'clinic_map_locations.png')


def main():
    m = yaml.safe_load(open(os.path.join(MAPS, 'clinic.yaml')))
    res, (ox, oy, _) = m['resolution'], m['origin']
    img = cv2.cvtColor(cv2.imread(os.path.join(MAPS, 'clinic.pgm'), cv2.IMREAD_GRAYSCALE), cv2.COLOR_GRAY2BGR)
    h = img.shape[0]
    scale = 2
    img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)

    def px(x, y):
        return int((x - ox) / res * scale), int((h - (y - oy) / res) * scale)

    loc = yaml.safe_load(open(LOCATIONS))
    for c in loc['containers']:
        if c.get('enabled', True):
            p = px(c['x'], c['y'])
            cv2.rectangle(img, (p[0] - 8, p[1] - 8), (p[0] + 8, p[1] + 8), (0, 200, 255), -1)
            cv2.putText(img, 'tag %d' % c['tag_id'], (p[0] + 14, p[1] + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 120, 160), 1)
    for name, l in loc['locations'].items():
        p = px(l['x'], l['y'])
        cv2.circle(img, p, 12, (0, 160, 0), 3)
        label = name.replace('collection_', 'Collection ').replace('_', ' ').title().replace('Collection ', 'Collection ')
        cv2.putText(img, label, (p[0] + 16, p[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 110, 0), 2)
    # crop to the area that matters (drop empty unknown margin)
    ys, xs = (img.sum(axis=2) < 3 * 250).nonzero()
    img = img[max(ys.min() - 20, 0):ys.max() + 20, max(xs.min() - 20, 0):xs.max() + 20]
    os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
    cv2.imwrite(OUT, img)
    print('wrote', os.path.abspath(OUT), img.shape[1], 'x', img.shape[0])


if __name__ == '__main__':
    main()
