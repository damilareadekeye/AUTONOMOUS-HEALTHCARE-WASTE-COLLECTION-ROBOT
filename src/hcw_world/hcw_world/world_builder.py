"""Turn the Open-RMF clinic world into a plain Gazebo world our robot can use.

The Open-RMF world has no Sensors/IMU system (needed for our LiDAR and camera) and
carries Open-RMF door/lift plugins we do not use. This module patches a copy of it.
The original files in rmf_demos_maps are never modified.

Profiles (how much of the clinic is loaded):
  full      both floors with all furniture and people      (very slow: camera/LiDAR render ~700 models)
  floor1    ground floor only, with furniture and people
  building  ground-floor building shell only, no furniture (fastest; add our own obstacles)
"""
import os
import re

import yaml
from ament_index_python.packages import get_package_share_directory

PROFILES = ('full', 'floor1', 'building')

SENSOR_SYSTEMS = """
    <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors">
      <render_engine>ogre2</render_engine>
    </plugin>
    <plugin filename="gz-sim-imu-system" name="gz::sim::systems::Imu">
    </plugin>
"""

# Open-RMF specific plugins: removed because we do not run Open-RMF.
_RMF_PLUGINS = [
    r'<plugin filename="libdoor\.so" name="door">\s*</plugin>',
    r'<plugin filename="liblift\.so" name="lift">\s*</plugin>',
    r'<plugin filename="toggle_charging" name="toggle_charging"\s*/>',
    r'<plugin name="toggle_floors" filename="toggle_floors">.*?</plugin>',
]

_INCLUDE = re.compile(r'<include>.*?</include>', re.DOTALL)
_MODEL_TAG = re.compile(r'<model\b[^>]*?(/?)>|</model>')


def _remove_jointed_models(text):
    """Remove every top-level <model> that contains a <joint> (doors, lift doors, lift cabins).

    Lift cabins contain nested models, so the tags are matched by depth, not by a simple pattern.
    """
    out, pos, depth, start = [], 0, 0, 0
    for m in _MODEL_TAG.finditer(text):
        if m.group(0) == '</model>':
            depth -= 1
            if depth == 0 and '<joint' in text[start:m.end()]:
                out.append(text[pos:start])
                pos = m.end()
        elif not m.group(1):                      # opening tag (self-closing ones are ignored)
            if depth == 0:
                start = m.start()
            depth += 1
    out.append(text[pos:])
    return ''.join(out)
_FLOOR2_MIN_Z = 5.0   # second-floor models sit about 10 m above the ground floor


def clinic_world_path():
    maps = get_package_share_directory('rmf_demos_maps')
    return os.path.join(maps, 'maps', 'clinic', 'clinic.world')


def resource_paths():
    """Folders that hold the models the clinic world refers to with model://."""
    maps = get_package_share_directory('rmf_demos_maps')
    assets = get_package_share_directory('rmf_demos_assets')
    # ~/.gazebo/models is where the rmf_demos_maps build downloads furniture and people models.
    ours = get_package_share_directory('hcw_world')
    return [os.path.join(maps, 'maps', 'clinic', 'models'),
            os.path.join(assets, 'models'),
            os.path.expanduser('~/.gazebo/models'),
            os.path.join(ours, 'models')]


def _keep(include, profile):
    uri = re.search(r'<uri>model://([^<]*)</uri>', include).group(1)
    if uri.startswith('Open-RMF/'):                  # demo robots: not installed, not wanted
        return False
    if profile == 'building':
        return uri == 'clinic_L1'
    if profile == 'floor1':
        pose = re.search(r'<pose>\s*\S+\s+\S+\s+(\S+)', include)
        return not (pose and float(pose.group(1)) > _FLOOR2_MIN_Z) and uri != 'clinic_L2'
    return True


def load_locations():
    """The named places and containers (hcw_world/config/locations.yaml)."""
    path = os.path.join(get_package_share_directory('hcw_world'), 'config', 'locations.yaml')
    with open(path) as f:
        return yaml.safe_load(f)


def container_includes(decoy=False):
    """<include> blocks for our AprilTag containers. The decoy (tag 14) is only added on request."""
    out = []
    for c in load_locations()['containers']:
        if not c.get('enabled', True) and not decoy:
            continue
        out.append('<include><name>hcw_container_%d</name><uri>model://hcw_container_%d</uri>'
                   '<pose>%s %s 0 0 0 %s</pose></include>\n'
                   % (c['tag_id'], c['tag_id'], c['x'], c['y'], c['yaw']))
    return ''.join(out)


def build_world(out_path, profile='floor1', containers=True, decoy=False):
    """Write the patched world to out_path and return out_path."""
    if profile not in PROFILES:
        raise ValueError('profile must be one of %s' % (PROFILES,))
    with open(clinic_world_path(), encoding='utf-8') as f:
        text = f.read()
    for pattern in _RMF_PLUGINS:
        text = re.sub(pattern, '', text, flags=re.DOTALL)
    # Every inline model with a joint is a door or a lift. Open-RMF opens them with a plugin we do
    # not run, so they would stay shut and block the doorways: remove them (doorways stay open).
    text = _remove_jointed_models(text)
    text = _INCLUDE.sub(lambda m: m.group(0) if _keep(m.group(0), profile) else '', text)
    # Furniture, people and the building never move: make them static so physics skips them.
    text = re.sub(r'(<include>\s*<name>[^<]*</name>)', r'\1<static>true</static>', text)
    marker = 'gz::sim::systems::SceneBroadcaster">'
    end = text.index('</plugin>', text.index(marker)) + len('</plugin>')
    text = text[:end] + SENSOR_SYSTEMS + text[end:]
    if containers:
        text = text.replace('</world>', container_includes(decoy) + '  </world>')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(text)
    return out_path
