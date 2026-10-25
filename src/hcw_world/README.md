# hcw_world

Builds the Gazebo world the simulation runs in: patches the Open-RMF clinic world (adds the
sensor/IMU systems our robot needs, and removes the Open-RMF door and lift plugins, the door
and lift models themselves, and the Open-RMF demo robots, which is why the doorways are open
in our simulation) and generates the AprilTag-marked container models used as collection
points.

This package has no launch file of its own; `hcw_bringup`'s `sim_clinic.launch.py` calls its
`build_world()` function directly to generate the world before starting Gazebo. It has no ROS
topics of its own at runtime, since its job is building the world file and models, not running
a node.

## Regenerate the container/tag models

```bash
python3 src/hcw_world/scripts/make_tag_models.py
```

## Important files
- `hcw_world/world_builder.py` — `build_world()`, `PROFILES` (`full`, `floor1`, `building`), `resource_paths()`
- `config/locations.yaml` — named locations (home, collection_A/B/C, storage), container poses,
  and the `drop_points` where the magnet puts containers down
- `scripts/make_tag_models.py` — regenerates the container and tag models
- `models/hcw_container_11` … `hcw_container_14` — the container models (tags 11–14)
