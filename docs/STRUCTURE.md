# Project Structure and Team Guide

Last updated: 2026-10-24

## 1. Folder map

```
~/hcw_ws/                        (this Git repository; keep it in the Linux home, not /mnt/c)
├── README.md
├── docs/
│   ├── 00_Quick_Start_Run_Workflow.md    how to run everything, step by step
│   ├── 01_Environment_Setup.md           install and GPU setup
│   ├── 02_Atlas_Autonomy_Evaluation.md   evaluation result (rejected)
│   ├── 03_OpenRMF_Clinic_World_Evaluation.md
│   ├── STRUCTURE.md                      this file
│   └── results/                          (later) test runs, tables, plots
├── scripts/
│   ├── env.sh                            source in every terminal
│   └── clean_sims.sh                     stop all simulations before starting a new one
└── src/
    ├── hcw_bringup/                      LAUNCH: the one place that starts things
    │   └── launch/sim_clinic.launch.py       clinic world + TurtleBot 4 + RViz
    ├── hcw_world/                        WORLD: clinic world and our own models
    │   ├── hcw_world/world_builder.py        patches the Open-RMF clinic world for our robot
    │   ├── worlds/                           (later) our own world files
    │   └── models/                           (later) AprilTag containers, collection-point markers
    ├── hcw_navigation/   (planned)       maps/*.yaml|pgm, nav2 params, named locations
    ├── hcw_perception/   (planned)       camera + apriltag_ros + verification node
    └── hcw_task/         (planned)       task manager (Nav2 Simple Commander, state machine)
```

Rule of thumb: **one package = one job**. Launch files live only in `hcw_bringup`.
Packages depend downwards (`hcw_task` uses navigation and perception; never the reverse).

## 2. How the pieces talk (target design)

```
 task request ──► hcw_task (state machine)
                    │ goal: "collection_point_A"           ▲ VERIFIED / not verified
                    ▼                                      │
              Nav2 (hcw_navigation)                  hcw_perception
                    │ /cmd_vel                         camera ► AprilTag ► verifier
                    ▼                                      ▲ /rgbd_camera/image
              TurtleBot 4 in Gazebo (hcw_world, hcw_bringup)
```
Rules: perception only publishes observations, never motor commands; Nav2 alone moves the robot;
a wrong or unstable detection leads to wait, retry or failure, never to unsafe motion.

## 3. Suggested ownership (edit names as the team agrees)

| Package | Job | Owner |
|---|---|---|
| hcw_bringup, hcw_world | Simulation and world | _name_ |
| hcw_navigation | Map, Nav2, named locations | _name_ |
| hcw_perception | Camera and AprilTag (Dami) | Dami |
| hcw_task | Task manager and tests | _name_ |

## 4. Working as a team (Git)

- `main` always builds and runs. Work on a branch: `git switch -c feature/<short-name>`, then open a pull request.
- Pull before you start: `git pull`. Commit small and often, with a clear message.
- Never commit `build/`, `install/`, `log/` (already in `.gitignore`), or large downloaded models.
- Each person uses a different `ROS_DOMAIN_ID` (see doc 01, section 6).
- Add a line to the relevant doc whenever you change how something is run.

## 5. Clinic assets (one-time setup, per machine)

Our clinic world comes from the Open-RMF demos. They are built once, outside this repository:
```bash
mkdir -p ~/eval/rmf_ws/src && cd ~/eval/rmf_ws/src
git clone -b jazzy https://github.com/open-rmf/rmf_demos.git
cd ~/eval/rmf_ws
sudo apt update && sudo apt install -y ros-jazzy-rmf-dev
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --continue-on-error      # about 5 min; downloads models to ~/.gazebo/models
```
`scripts/env.sh` sources this workspace automatically if it exists. Our code never edits it: the
world is patched in memory at launch time (`world_builder.py`) and written to `/tmp/hcw_clinic.sdf`.

What the patch does: adds the Sensors and IMU systems (LiDAR and camera need them), removes the
Open-RMF door/lift plugins and demo robots, and marks all models static so physics ignores
them (otherwise the simulation runs at about 1 % real time).

## 6. Where to put new work

| New thing | Goes in |
|---|---|
| A new launch combination | `hcw_bringup/launch/` |
| A map, Nav2 parameter file, location list | `hcw_navigation/` |
| A Gazebo model (container, tag, obstacle) | `hcw_world/models/` |
| A node (Python) | the package it belongs to, under `<package>/<package>/` |
| Test results | `docs/results/` |
