# hcw_navigation

Holds the saved map of the clinic, the Nav2 and SLAM Toolbox configuration, and the `go_to`
command for sending the robot to named locations.

## Run

Navigate on the saved map (start the simulation first):
```bash
ros2 launch hcw_navigation navigation.launch.py
ros2 launch hcw_navigation navigation.launch.py rviz:=True
```

Build a new map instead:
```bash
ros2 launch hcw_navigation mapping.launch.py
ros2 run hcw_navigation map_clinic          # drives the clinic corridors and saves the map
```

Send the robot to named places:
```bash
ros2 run hcw_navigation go_to collection_A
ros2 run hcw_navigation go_to collection_A collection_B storage home
```

The robot must start at the home spot (8.0, -31.7); restart the simulation before restarting
Nav2, otherwise the robot and AMCL disagree about where the robot is.

## Important files
- `launch/navigation.launch.py` — Nav2 on the saved map (AMCL localisation)
- `launch/mapping.launch.py` — SLAM Toolbox + Nav2 for building a new map
- `hcw_navigation/go_to.py` — sends the robot to named places from `locations.yaml`
- `hcw_navigation/map_clinic.py` — drives the clinic corridors while mapping
- `maps/clinic.yaml` + `clinic.pgm` — the saved map
- `config/nav2_params.yaml`, `config/slam_mapping.yaml` — Nav2 and SLAM settings
- `scripts/seal_room_doors.py` — blocks consulting-room doorways on the map
- `scripts/plot_map.py` — draws the map with named places

## Topics
Uses Nav2's `NavigateToPose` action via the Nav2 Simple Commander (`BasicNavigator`), called
with `localizer='bt_navigator'` so `waitUntilNav2Active()` does not reset AMCL's pose.
