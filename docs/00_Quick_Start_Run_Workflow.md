# 00 — Quick Start: Run the Whole Workflow From a Fresh Session

Autonomous Healthcare-Waste Collection Robot — IEEE Rwanda Mentorship Program
Last updated: 2026-10-24

Read this first. It assumes the software is already installed (ROS 2 Jazzy, Gazebo Harmonic, Nav2,
`ros-jazzy-rmf-dev`; see `01_Environment_Setup.md` if not). It tells you how to start a session,
re-run every check we have passed so far, find where we stopped, and continue.

Everything below runs in the **Ubuntu (WSL) terminal** unless it says PowerShell.

---

## 1. Where we are

| Item | State |
|---|---|
| Environment (WSL2, GPU, ROS 2 Jazzy, Gazebo Harmonic 8.15.0, Nav2 1.3.13) | Done, verified |
| Test B: official Nav2 TurtleBot 4 depot simulation | Passed |
| Test A: Gazebo camera sensors (RGB, depth, RGB-D, thermal) | Passed |
| Atlas-Autonomy | Evaluated, rejected (does not build). Not used. |
| Open-RMF Clinic World | Runs with our TurtleBot at real-time speed (doc 04); Nav2 test passed (doc 03, Step 2) |
| World decision | **Clinic ground floor (L1) shell: decided 2026-10-24** |
| Map (SLAM Toolbox), named locations (home, A, B, C, storage) | Done (doc 05) |
| Camera, AprilTag containers, tag detection (ids 11, 12, 13) | Done: 9 of 9 correct detections (doc 05) |
| Navigation to every named place | Done: 15 of 15 legs over three loops (doc 05) |
| Task manager (state machine), verification rule, simulated magnet, missing and wrong container handling | Done in a first session (doc 08); obstacle case, repeated runs still to do |
| 20 to 30 repeated test runs, final documentation | Week 4 |

Target: baseline finished **2026-11-08**, review meeting week of **2026-11-09**.

**Fastest way to see everything work:** `scripts/clean_sims.sh && scripts/test_all_places.sh`
(starts the simulation, Nav2 and tag detection, then drives home, A, B, C, storage, home; about 6 minutes).
Details: `05_Mapping_Navigation_Perception.md`.

## 2. Start of every session (checklist)

### 2.1 Windows PowerShell
```powershell
wsl -l -v          # Ubuntu must show VERSION 2
wsl --update       # only occasionally
```
Open Ubuntu from the Start menu (or `wsl -d Ubuntu`).

### 2.2 Ubuntu: sanity checks (about 30 seconds)
```bash
glxinfo -B | grep "OpenGL renderer"     # must say D3D12 (NVIDIA GeForce RTX 3070 ...), NOT llvmpipe
nvidia-smi | head -5                    # must list the RTX 3070
echo $ROS_DISTRO                        # must print: jazzy
echo $ROS_DOMAIN_ID                     # must print your unique number (see 2.3)
```
If `glxinfo` shows `llvmpipe` or `Intel`, fix it first: `01_Environment_Setup.md`, Sections 3.2 and 7.

### 2.3 One-time settings (skip if already done)
```bash
echo 'export ROS_DOMAIN_ID=11' >> ~/.bashrc      # pick your own number, 0-101
grep -E "GALLIUM_DRIVER|MESA_D3D12|ros/jazzy" ~/.bashrc    # all three lines must exist
source ~/.bashrc
```

### 2.4 Get the latest project files
```bash
cd ~/hcw_ws && git pull
```

### 2.5 Rule: one simulation at a time
Two running simulations clash (`Found additional publishers on /stats, /clock`). Before starting any
simulation, and when you finish:
```bash
pkill -f "gz sim"; pkill -f ros2; pkill -f rviz2
```
Always use a **new terminal** per simulation, and do not `source` more than one evaluation
workspace in the same terminal.

## 3. Re-run the checks that already passed

### 3.1 Official Nav2 baseline (Test B)
```bash
ros2 launch nav2_bringup tb4_simulation_launch.py headless:=False
```
Gazebo and RViz open. Wait until RViz shows the map. Then:
1. RViz toolbar: **2D Pose Estimate**, click and drag on the robot's location in the map.
2. RViz toolbar: **Nav2 Goal**, click and drag at a free spot. The robot should drive there.

Expected: real-time factor about 100 %, RViz about 30 fps, Nav2 Navigation and Localization both `active`.
Stop with `Ctrl+C`, then run the cleanup line from 2.5.

### 3.2 Gazebo camera sensors (Test A)
```bash
pkill -f "gz sim"; pkill -f ros2
gz sim -v 3 sensors_demo.sdf
```
Press Play. RGB, depth, RGB-D and thermal panels must show live images (real-time factor about 60 %
with five cameras). Warnings about `Ogre2Camera::SetVisibilityMask`, `emission texture` and
`QML RowLayout` are harmless.

### 3.3 Open-RMF Clinic World (already built in `~/eval/rmf_ws`)
Use a **new terminal**:
```bash
cd ~/eval/rmf_ws
source install/setup.bash
ros2 launch rmf_demos_gz clinic.launch.xml
```
RViz shows "Clinic A & B layout plan" with blue navigation lanes. Gazebo should open the 3D clinic.
Record: does Gazebo show the clinic, what is the real-time factor, any red errors in the terminal?
Write results into `03_OpenRMF_Clinic_World_Evaluation.md`.

If `install/` is missing (a fresh machine), rebuild first:
```bash
mkdir -p ~/eval/rmf_ws/src && cd ~/eval/rmf_ws/src
git clone -b jazzy https://github.com/open-rmf/rmf_demos.git
cd ~/eval/rmf_ws
sudo apt update && sudo apt install -y ros-jazzy-rmf-dev
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --continue-on-error 2>&1 | tee build.log     # about 5 minutes
```
Note: do **not** add `~/eval/*/install/setup.bash` to `~/.bashrc`.

## 4. The path from here to the finished baseline

Each step ends with a commit. Do them in order.

| # | Step | Output | Acceptance |
|---|---|---|---|
| 1 | Finish the Clinic World evaluation (3.3, then doc 03 Step 2) | World decision written in doc 03 | Clinic L1 usable with Nav2, **or** office world chosen |
| 2 | Create ROS packages in `~/hcw_ws/src` (`hcw_world`, `hcw_robot`, `hcw_nav`, `hcw_perception`, `hcw_task`) | Packages that build with `colcon build` | `colcon build` passes |
| 3 | Robot with 2D LiDAR and one camera in the chosen world | Robot spawns, drives with `teleop_twist_keyboard` | Sensor topics visible: `ros2 topic list` |
| 4 | Map the world with SLAM Toolbox, save the map | `map.yaml` and `map.pgm` in `hcw_nav/maps/` | Nav2 localizes on the saved map |
| 5 | Define named locations: collection points A, B, C, storage point, home | `locations.yaml` | Robot reaches each by name |
| 6 | AprilTag containers (tags 11, 12, 13) and `apriltag_ros` | `/detections` publishes tag IDs | Correct ID seen when the robot is at the point |
| 7 | Verification rule: expected tag seen for N consecutive frames, then `VERIFIED` | `hcw_perception` verifier node | Wrong or missing tag does not give `VERIFIED` |
| 8 | Task manager: Nav2 Simple Commander plus state machine | `hcw_task` node | Idle, receive task, go to point, verify, attach, go to storage, release, report, return home |
| 9 | Simulated attach and release | Simplest reliable method (documented) | Container moves with the robot, then stays at storage |
| 10 | 20 to 30 repeated runs incl. wrong-container and obstacle cases | `results/` CSV and summary | Success rate, time per stage, failures and causes |
| 11 | Final write-up and README | docs updated | Another member can reproduce from this file |

Design rules (from the mentor and the perception plan):
- Perception only publishes observations. It never sends motor commands.
- Nav2 alone is responsible for motion and obstacle avoidance.
- A wrong or unstable detection leads to wait, retry or failure report, never to unsafe motion.
- AprilTag is the baseline. YOLO is an optional later experiment.

## 5. Build and run our own workspace (once packages exist)
```bash
cd ~/hcw_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install 2>&1 | tee build.log
source install/setup.bash
```
Add `source ~/hcw_ws/install/setup.bash` to `~/.bashrc` only after the first successful build.
Launch commands for our own simulation will be added here as each step above is completed.

## 6. Saving work (Git)
```bash
cd ~/hcw_ws
git status
git add docs src
git commit -m "Short description of what changed"
git push
```
`gh` is already logged in on this machine (`gh auth status`). Never commit `build/`, `install/` or
`log/` (already in `.gitignore`). Keep the project under `~/`, not `/mnt/c/`.

## 7. Quick troubleshooting

| Symptom | Fix |
|---|---|
| `llvmpipe` in `glxinfo` | Add user to `video,render`, `wsl --shutdown` in PowerShell, check the two `export` lines in `~/.bashrc` |
| Gazebo or RViz window does not appear | `wsl --update`, then `wsl --shutdown` and reopen Ubuntu |
| `Found additional publishers on /stats, /clock` | Run the cleanup line in 2.5 |
| `Package '...' not found` | The terminal did not source the right workspace: `source install/setup.bash` in that workspace |
| Robot does not move after setting a Nav2 goal | Set **2D Pose Estimate** first; wait until Nav2 shows `active` |
| `sudo` asks for a password | Type your Ubuntu password; it shows nothing while typing |
| Group change has no effect | `wsl --shutdown` in PowerShell, not just closing the terminal |

For anything else see `01_Environment_Setup.md`, Section 7.
