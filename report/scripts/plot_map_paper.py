"""Draw the clinic map with the named places for the paper (vector PDF, 8 pt labels).

    python scripts/plot_map_paper.py <clinic.pgm> <clinic.yaml> <locations.yaml> <out.pdf>

Defaults assume the repository layout (src/hcw_navigation/maps, src/hcw_world/config) next to the report folder.
"""
import os
import re
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'hcw_ws'))
pgm, ymlp, locp, out = (sys.argv[1:5] + [None] * 4)[:4]
pgm = pgm or r'\\wsl.localhost\Ubuntu\home\damilare\hcw_ws\src\hcw_navigation\maps\clinic.pgm'
ymlp = ymlp or pgm.replace('clinic.pgm', 'clinic.yaml')
locp = locp or r'\\wsl.localhost\Ubuntu\home\damilare\hcw_ws\src\hcw_world\config\locations.yaml'
out = out or os.path.join(HERE, '..', '..', 'report', 'figures', 'clinic_map.pdf')

yml = open(ymlp).read()
res = float(re.search(r'resolution:\s*([\d.]+)', yml).group(1))
ox, oy = [float(v) for v in re.search(r'origin:\s*\[([^\]]+)\]', yml).group(1).split(',')[:2]]
img = np.array(Image.open(pgm).convert('L'))
h, w = img.shape
loc = {}
for name, x, y in re.findall(r'^\s{2}(home|collection_[ABC]|storage):\s*\{x:\s*([-\d.]+),\s*y:\s*([-\d.]+)', open(locp).read(), flags=re.M):
    loc[name] = (float(x), float(y))
known = np.argwhere(img != 205)
r0, c0 = known.min(axis=0) - 6
r1, c1 = known.max(axis=0) + 6
c0 = c0 - 24                  # extra room on the left for the "Home" label
r0 = max(r0, 0)
PAD = 0
if c0 < 0:                    # pad with the 'unknown' gray if the image has no more margin on the left
    PAD = -c0
    img = np.pad(img, ((0, 0), (PAD, 0)), constant_values=205)
    c0, c1 = 0, c1 + PAD


def px(x, y):
    return (x - ox) / res + PAD - c0, (h - (y - oy) / res) - r0


fig = plt.figure(figsize=(1.40, 1.30))
ax = fig.add_axes([0, 0, 1, 1])
ax.imshow(img[r0:r1, c0:c1], cmap='gray', vmin=0, vmax=255)
labels = {'home': 'Home', 'collection_A': 'A', 'collection_B': 'B', 'collection_C': 'C', 'storage': 'Storage'}
# label offsets in points: (dx, dy, horizontal alignment)
offsets = {'home': (-3, -10, 'left'), 'collection_A': (6, 0, 'left'), 'collection_B': (6, 0, 'left'),
           'collection_C': (6, 0, 'left'), 'storage': (-5, 8, 'right')}
for k, (x, y) in loc.items():
    cx, cy = px(x, y)
    ax.plot(cx, cy, 'o', ms=4.5, mfc='#d62828', mec='white', mew=0.6)
    dx, dy, ha = offsets[k]
    ax.annotate(labels[k], (cx, cy), xytext=(dx, dy), textcoords='offset points', fontsize=8, fontweight='bold',
                color='#b00000', va='center', ha=ha, bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none', alpha=0.85))
ax.set_xlim(0, c1 - c0)
ax.set_ylim(r1 - r0, 0)
ax.axis('off')
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
fig.savefig(out)
print('wrote', os.path.abspath(out), 'places:', sorted(loc))
