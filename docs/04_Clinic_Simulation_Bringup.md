# 04 — Clinic World + TurtleBot 4 Bring-up

Last updated: 2026-10-24

Our own simulation (not the Open-RMF launch): the Open-RMF clinic world with a TurtleBot 4,
started by `hcw_bringup`. This is the simulation layer that Nav2, SLAM and the task manager build on.

## Run

```bash
cd ~/hcw_ws
source scripts/env.sh                       # every new terminal
colcon build --symlink-install              # only after pulling changes
scripts/clean_sims.sh                       # stop any other simulation first
ros2 launch hcw_bringup sim_clinic.launch.py
```

Gazebo and RViz open. The robot starts at (8.0, -31.7), the "L1_sub_waiting_area_1" parking spot.

Options:

| Argument | Default | Meaning |
|---|---|---|
| `profile` | `building` | `building` = ground-floor shell only (fast); `floor1` = plus furniture and people (about 3 % real time); `full` = both floors (about 1 % real time) |
| `headless` | `False` | `True` = no Gazebo window and no RViz |
| `x_pose`, `y_pose`, `yaw` | 8.0, -31.7, 0.0 | start pose in the world |

## Move the robot with the arrow keys

```bash
source ~/hcw_ws/scripts/env.sh
ros2 run hcw_bringup teleop_arrows
```
Up / Down = forward / back, Left / Right = turn, Space = stop, `+` / `-` = faster / slower, `q` = quit.
Hold a key to keep moving (the robot stops about 0.5 s after you let go). Click inside that terminal
first: it only reads keys from its own window. It must be a terminal that ran `source scripts/env.sh`
(same `ROS_DOMAIN_ID` as the simulation). Source: `hcw_bringup/hcw_bringup/teleop_arrows.py`.

## Move the robot (other ways, check that it works)

```bash
source ~/hcw_ws/scripts/env.sh
sudo apt install -y ros-jazzy-teleop-twist-keyboard         # once
ros2 run teleop_twist_keyboard teleop_twist_keyboard        # i = forward, j/l = turn, k = stop
# or one command: drive forward at 0.3 m/s
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}}"
```

Topics: `/cmd_vel` (input), `/odom`, `/scan` (LiDAR), `/imu`, `/rgbd_camera/image`,
`/rgbd_camera/depth_image`, `/tf`, `/clock`.

## Results (2026-10-24, reference machine: RTX 3070 laptop, WSL2)

| Check | Result |
|---|---|
| Clinic world loads in Gazebo Harmonic, TurtleBot 4 spawns | Pass |
| Robot drives: `/cmd_vel` 0.3 m/s for 6 s gives about 0.95 m on `/odom` | Pass |
| `profile=building`: real-time factor | 1.00; LiDAR about 9.8 Hz (headless), steady 1.0 with Gazebo and RViz open |
| `profile=floor1` (405 models): real-time factor | 0.03; LiDAR 2.5 Hz |
| `profile=full` (708 models): real-time factor | 0.013 to 0.02 |
| Clinic world alone without a robot or sensors, all 708 models | 0.99 |

## Findings and fixes (read before changing the world)

1. **The file `clinic.rviz` is only an RViz layout.** The Gazebo world is `clinic.world`
   (in `rmf_demos_maps`). Our launch uses that.
2. **Open-RMF world has no Sensors/IMU system**, so a robot with LiDAR and camera shows no data.
   `world_builder.py` adds both.
3. **Open-RMF demo robots and door/lift plugins** are not installed or needed: removed.
4. **Furniture models live in `~/.gazebo/models`** (downloaded by the rmf_demos_maps build); the
   launch adds that folder to `GZ_SIM_RESOURCE_PATH`.
5. **Speed:** physics is not the problem (world alone runs at 0.99). The robot's camera and LiDAR
   rendering hundreds of detailed models is. Hence the `building` default. Furniture is added
   back selectively as our own light obstacles and containers (in `hcw_world/models/`).
6. **Do not use Nav2's `simulation.launch.py` with this world:** it converts the world with xacro while Gazebo
   already starts, and the large file loses that race (Gazebo dies with "Unable to find or download file").
7. `scripts/clean_sims.sh` uses specific patterns on purpose. A plain `pkill -f ros2` also kills the
   terminal that runs it.

## Troubleshooting: RViz opens but there is no Gazebo window

Symptom: the launch starts and RViz opens, but no Gazebo window appears. The simulation is actually
running (`gz topic -e -t /stats -n 1 | grep real_time_factor` answers). The Gazebo window process
(`gz sim -v4 -g`) had started together with the server and exited silently. Fixed on 2026-10-24:
the launch now starts the window 8 s after the server. If it still happens, open the window by hand
in a new terminal: `source ~/hcw_ws/scripts/env.sh && gz sim -v4 -g`, then wait up to a minute.

## Troubleshooting: simulation slows down while driving

Measured 2026-10-24 on the reference machine, `profile=building`, Gazebo window and RViz open:
average real-time factor 0.33; with RViz closed, 0.73. RViz (with its camera and depth displays) is
costly. Do not open more than one Gazebo window: a second `gz sim -g` renders the whole scene again
(`ps -eo args | grep "gz sim -v4 -g"` must show one). Close RViz when you do not need it, and
disable its camera and depth image displays.

## Next

Drive the robot around the building and judge whether the ground floor is usable with Nav2
(doc 03, Step 2): map with SLAM Toolbox, then navigate to named locations.
