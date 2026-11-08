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


# Rooms that get props. The door of each room is a model in the clinic world; its position is read from there.
# Curved west-wing rooms (outer column, x about 14 to 16): the room lies east of the door. Straight columns:
# the door's yaw (+-1.57) tells which side the room is on (checked against the map for the left inner column).
# Corner and slanted rooms are skipped: their shape is not known.
_CURVED_ROOMS = (8, 9, 10, 11, 12)           # left outer column
_ROOM_SIDE = [                                # (side, rooms, direction into the room: +1 east, -1 west)
    ('left', (2, 3, 4, 5), -1),
    ('right', (9, 10, 11, 12, 13), +1),
    ('right', (3, 4, 5), -1),
]


def _consult_doors(text):
    """[(side, room number, x, y)] for the consulting-room doors of the original world."""
    pat = re.compile(r'<model name="L1_(left|right)_consult_rm_(\d+)_outer">\s*<pose>([^<]*)</pose>')
    out = []
    for m in pat.finditer(text):
        v = [float(s) for s in m.group(3).split()]
        out.append((m.group(1), int(m.group(2)), v[0], v[1]))
    return out


def _box(name, size_uv, uv, z, rgb, direction, door):
    """A box in the room frame: u goes from the door into the room, v is sideways."""
    x, y = door[0] + direction * uv[0], door[1] + uv[1]
    return ('<visual name="%s"><pose>%.3f %.3f %.3f 0 0 0</pose><geometry><box><size>%s %s %s</size></box></geometry>'
            '<material><ambient>%s %s %s 1</ambient><diffuse>%s %s %s 1</diffuse></material></visual>'
            % ((name, x, y, z) + tuple(size_uv) + tuple(rgb) + tuple(rgb)))


def _cyl(name, radius, length, uv, rgb, direction, door):
    x, y = door[0] + direction * uv[0], door[1] + uv[1]
    return ('<visual name="%s"><pose>%.3f %.3f %.3f 0 0 0</pose><geometry><cylinder><radius>%s</radius><length>%s</length>'
            '</cylinder></geometry><material><ambient>%s %s %s 1</ambient><diffuse>%s %s %s 1</diffuse></material></visual>'
            % ((name, x, y, length / 2.0, radius, length) + tuple(rgb) + tuple(rgb)))


def _layout(kind, d, door):
    """Visuals of one room. Sizes are (along u, along v, height); z is the box centre height."""
    B = lambda n, s, uv, z, c: _box(n, (s[0], s[1], s[2]), uv, z, c, d, door)
    if kind == 'office':
        return [B('desk', (0.6, 1.4, 0.75), (3.5, 0.0), 0.375, (0.60, 0.45, 0.30)),
                B('monitor', (0.05, 0.45, 0.30), (3.5, 0.0), 0.90, (0.10, 0.10, 0.12)),
                B('chair', (0.45, 0.45, 0.45), (2.8, 0.0), 0.225, (0.20, 0.25, 0.35)),
                B('filing', (0.5, 0.4, 1.2), (3.7, 1.2), 0.6, (0.60, 0.62, 0.65)),
                _cyl('bin', 0.18, 0.5, (2.2, -1.0), (0.95, 0.80, 0.10), d, door)]
    visuals = [B('bed', (2.0, 0.9, 0.35), (2.7, 0.0), 0.175, (0.92, 0.92, 0.95)),
               B('blanket', (1.4, 0.9, 0.10), (2.5, 0.0), 0.40, (0.15, 0.40, 0.80)),
               B('pillow', (0.35, 0.5, 0.10), (3.45, 0.0), 0.40, (1.0, 1.0, 1.0))]
    if kind == 'treatment':
        visuals += [_cyl('iv_stand', 0.03, 1.8, (2.2, 0.75), (0.75, 0.75, 0.78), d, door),
                    B('trolley', (0.5, 0.4, 0.8), (1.9, -0.85), 0.4, (0.70, 0.72, 0.75))]
    else:                                                       # patient room
        visuals += [B('cabinet', (0.4, 0.4, 0.6), (3.4, 0.75), 0.3, (0.55, 0.65, 0.60)),
                    B('chair', (0.4, 0.4, 0.45), (2.2, -0.9), 0.225, (0.55, 0.35, 0.20)),
                    _cyl('bin', 0.18, 0.5, (3.7, -0.9), (0.95, 0.80, 0.10), d, door)]
    return visuals


def prop_models(doors):
    """Simple hospital-room props from flat-coloured boxes and cylinders: patient rooms, offices, treatment rooms.

    Visual only (no collision, no physics cost). The robot's LiDAR and camera still see them (tested: the
    window-only visibility flag does not hide them from the LiDAR), so they are an option (`props:=True`),
    not part of the tested default world.
    """
    by_key = {(side, n): (x, y) for side, n, x, y in doors}
    rooms = [(('left', n), +1) for n in _CURVED_ROOMS]
    for side, numbers, d in _ROOM_SIDE:
        rooms += [((side, n), d) for n in numbers]
    out = []
    for i, (key, d) in enumerate(rooms):
        if key not in by_key:
            continue
        kind = ('patient', 'office', 'treatment')[i % 3]
        out.append('<model name="hcw_prop_%s_%d"><static>true</static><link name="l">%s</link></model>\n'
                   % (key[0], key[1], ''.join(_layout(kind, d, by_key[key]))))
    out.append(_storage_area())
    return ''.join(out)


# North wall of the storage bay (y, from the saved map: solid for x from 26 to 34.5).
_NORTH_WALL_Y = -10.63


def _vbox(name, size, xyz, rgb):
    """A box at a world position, flat colour, visual only."""
    return ('<visual name="%s"><pose>%.3f %.3f %.3f 0 0 0</pose><geometry><box><size>%s %s %s</size></box></geometry>'
            '<material><ambient>%s %s %s 1</ambient><diffuse>%s %s %s 1</diffuse></material></visual>'
            % ((name,) + tuple(xyz) + tuple(size) + tuple(rgb) + tuple(rgb)))


def _vcyl(name, radius, length, xyz, rgb):
    """A vertical cylinder at a world position (xyz = centre), flat colour, visual only."""
    return ('<visual name="%s"><pose>%.3f %.3f %.3f 0 0 0</pose><geometry><cylinder><radius>%s</radius><length>%s</length>'
            '</cylinder></geometry><material><ambient>%s %s %s 1</ambient><diffuse>%s %s %s 1</diffuse></material></visual>'
            % ((name,) + tuple(xyz) + (radius, length) + tuple(rgb) + tuple(rgb)))


def _storage_area():
    """The hazardous-waste storage area: shelves, warning decal and signs, bins and posts. Visual only.

    The drop point (locations.yaml, drop_points.storage) is tucked against the north wall between the shelves. The
    robot stops 0.55 m south of it. Everything else is kept out of the robot's route (it arrives from the west and
    leaves to the west). The floor decal is 2 cm high, below the LiDAR plane (about 30 cm): only a marking.
    Textures: hcw_world/scripts/make_hazard_textures.py.
    """
    drop = load_locations()['drop_points']['storage']
    cx = float(drop['x'])
    pad_y = _NORTH_WALL_Y - 0.85
    yellow, orange, red = (0.95, 0.75, 0.10), (0.95, 0.50, 0.10), (0.80, 0.15, 0.15)
    cartons = [yellow, orange, red]
    visuals = []
    unit_y = _NORTH_WALL_Y - 0.175
    for i, dx in enumerate((-2.9, -1.4, 1.4, 2.9)):                      # 4 shelf units, 1.4 m long, 0.1 m apart
        x = cx + dx
        visuals.append(_vbox('shelf%d' % i, (1.4, 0.35, 1.8), (x, unit_y, 0.9), (0.25, 0.28, 0.33)))
        for j, (off, z) in enumerate(((-0.40, 0.35), (0.10, 0.95), (0.40, 1.50))):
            visuals.append(_vbox('carton%d_%d' % (i, j), (0.45, 0.20, 0.35), (x + off, _NORTH_WALL_Y - 0.45, z),
                                 cartons[(i + j) % 3]))
    for k, bx in enumerate((cx + 2.4, cx + 3.0)):                        # two yellow clinical-waste bins, east end
        visuals.append(_vcyl('bin%d' % k, 0.25, 0.85, (bx, pad_y - 0.1, 0.425), yellow))
        visuals.append(_vcyl('binlid%d' % k, 0.26, 0.08, (bx, pad_y - 0.1, 0.89), (0.12, 0.12, 0.12)))
    visuals.append(_vbox('sharps', (0.30, 0.30, 0.40), (cx + 3.5, _NORTH_WALL_Y - 0.65, 0.20), red))
    for k, px_ in enumerate((cx - 3.6, cx + 3.6)):                       # corner posts at the south corners of the zone
        visuals.append(_vcyl('post%d' % k, 0.05, 1.1, (px_, _NORTH_WALL_Y - 1.7, 0.55), yellow))
        visuals.append(_vcyl('postband%d' % k, 0.052, 0.20, (px_, _NORTH_WALL_Y - 1.7, 0.90), (0.08, 0.08, 0.08)))
    model = '<model name="hcw_prop_storage"><static>true</static><link name="l">%s</link></model>\n' % ''.join(visuals)
    decal = ('<include><name>hcw_hazard_floor</name><uri>model://hcw_hazard_floor</uri>'
             '<pose>%.3f %.3f 0.02 0 0 0</pose></include>\n' % (cx, pad_y))
    signs = ''.join('<include><name>hcw_hazard_sign_%d</name><uri>model://hcw_hazard_sign</uri>'
                    '<pose>%.3f %.3f 2.2 0 0 0</pose></include>\n' % (i, cx + dx, _NORTH_WALL_Y - 0.03)
                    for i, dx in enumerate((-1.4, 1.4)))
    return model + decal + signs


def build_world(out_path, profile='floor1', containers=True, decoy=False, props=False):
    """Write the patched world to out_path and return out_path."""
    if profile not in PROFILES:
        raise ValueError('profile must be one of %s' % (PROFILES,))
    with open(clinic_world_path(), encoding='utf-8') as f:
        text = f.read()
    doors = _consult_doors(text)           # before the door models are removed below
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
    if props:
        text = text.replace('</world>', prop_models(doors) + '  </world>')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(text)
    return out_path
