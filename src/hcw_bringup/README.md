# hcw_bringup

Starts the Gazebo Harmonic simulation of the Open-RMF clinic world with a TurtleBot 4 spawned
inside it. This is the simulation layer only; Nav2, mapping and perception are started separately.

## Run

```bash
cd ~/hcw_ws
source scripts/env.sh                       # every new terminal
colcon build --symlink-install               # only after pulling changes
scripts/clean_sims.sh                        # stop any other simulation first
ros2 launch hcw_bringup sim_clinic.launch.py
```

Useful options: `profile:=building|floor1|full`, `gui:=True` (open the Gazebo window),
`rviz:=True`, `headless:=True`, `decoy:=True` (also place the wrong container, tag 14),
`x_pose:=`, `y_pose:=`, `yaw:=`.

## Drive the robot manually

```bash
source ~/hcw_ws/scripts/env.sh
ros2 run hcw_bringup teleop_arrows
```
Arrow keys to drive, Space to stop, `+`/`-` to change speed, `q` to quit. Click inside the
terminal window first.

Other ways to move the robot:
```bash
source ~/hcw_ws/scripts/env.sh
sudo apt install -y ros-jazzy-teleop-twist-keyboard
ros2 run teleop_twist_keyboard teleop_twist_keyboard
# or:
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}}"
```

## Important files
- `launch/sim_clinic.launch.py` — starts Gazebo, spawns the robot, optionally opens RViz
- `hcw_bringup/teleop_arrows.py` — arrow-key driving tool

## Topics
`/cmd_vel` (input), `/odom`, `/scan`, `/imu`, `/rgbd_camera/image`, `/rgbd_camera/depth_image`,
`/tf`, `/clock`.
