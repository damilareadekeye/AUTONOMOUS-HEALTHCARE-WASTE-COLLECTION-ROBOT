# Project Structure — How the Project Sits on Dami's Machine

Autonomous Healthcare-Waste Collection Robot — IEEE Rwanda Mentorship Program
Team: **Dami**, **Beni**, **David**
Last updated: 2026-10-24 · Repository: https://github.com/damilareadekeye/AUTONOMOUS-HEALTHCARE-WASTE-COLLECTION-ROBOT

Purpose of this file: any teammate can read it and know exactly what is installed on Dami's machine
(the only machine running the project today), where every file lives, how to run it, where the
project stands against the schedule, and what is left to do.

---

## 1. The project in one paragraph

A simulated indoor robot receives a waste-collection task, drives to a collection point in a
hospital-like building, checks the container with its camera (AprilTag marker), "attaches" it,
carries it to the storage point, releases it, reports completion and returns home. Everything runs
in simulation first. The robot never handles real waste; the scope is transport of sealed containers.

Design rules (from the mentor and the research PDFs):
- Perception only **publishes observations**; it never sends motor commands.
- **Nav2 alone** moves the robot and avoids obstacles.
- A wrong or unstable detection leads to wait, retry or "failed", never to unsafe motion.
- AprilTag is the baseline (no training data). YOLO is an optional later experiment.
- Success is measured by **end-to-end task success rate** over 20 to 30 repeated runs.

## 2. The machine

| Item | Value |
|---|---|
| Laptop | Gigabyte AORUS 15 SE (Dami's), Windows 11 Home |
| GPUs | NVIDIA RTX 3070 Laptop (8 GB) used for Gazebo, plus Intel Iris Xe (not used) |
| CPU threads / RAM | 20 threads, about 19 GB RAM visible to WSL |
| Linux | Ubuntu 24.04.5 LTS inside **WSL2** (distro name `Ubuntu`, Linux user `damilare`) |
| WSL kernel | 6.18.54.1-microsoft-standard-WSL2 |
| Disk | WSL virtual disk 1 TB, about 8 GB used |
| GPU in WSL | OpenGL via D3D12 (`GALLIUM_DRIVER=d3d12`, `MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA`), user in groups `video` and `render` |
| Windows driver | NVIDIA 561.09 (CUDA 12.6). Never install an NVIDIA driver inside WSL. |
| Python | 3.12.3 (system Python, no conda) |
| `ROS_DOMAIN_ID` | 11 (each teammate must use a different number, 0 to 101) |
| Git / GitHub | `gh` logged in as `damilareadekeye`; remote `origin` = the repository above |

### 2.1 Software stack (frozen versions)

| Component | Version |
|---|---|
| ROS 2 | Jazzy Jalisco (`ros-jazzy-desktop` 0.11.0) |
| Simulator | Gazebo Harmonic (Gazebo Sim 8.15.0) via `ros-jazzy-ros-gz` 1.0.24 |
| Navigation | Nav2 1.3.13 (`ros-jazzy-navigation2`, `ros-jazzy-nav2-bringup`) |
| Robot model | TurtleBot 4 from `nav2_minimal_tb4_sim` / `nav2_minimal_tb4_description` |
| Open-RMF | `ros-jazzy-rmf-dev` (only used for the clinic world files) |
| Mesa | 25.2.8 |

Do not install Gazebo Classic and do not upgrade Ubuntu. Same stack for everyone.

### 2.2 Why WSL2 and not a separate machine

Windows is only the host (VS Code, browser, PDFs). All robotics software runs in Ubuntu. Gazebo and
RViz windows appear on the Windows desktop through WSLg. Files for the project must live in the Linux
home folder (`~/`), not under `/mnt/c/`, or builds become slow and permissions break.

## 3. Where everything lives

### 3.1 On the Windows side

```
C:\Users\Aorus15\Desktop\ieee-robotics\          (this folder: planning documents, not code)
├── project_structure.md                         this file
├── text.txt                                     the mentor's instructions
├── Proposal.pdf                                 original project proposal (partly outdated: describes a physical robot)
├── Baseline_Implementation_Timeline.pdf         our schedule submitted to the mentor (4 weeks, due Nov 8)
├── Navigation_and_Simulation_Research_Findings.pdf
├── Existing Hospital _ Indoor Delivery Robots + Task Handling (1).pdf
├── Dami_Camera_Perception_and_Data_Plan_Healthcare_Waste_Robot(1).pdf
└── docs\                                        copies of docs 01 to 03
```
VS Code opens this folder, or the Ubuntu one through the WSL extension ("Connect to WSL", then open `~/hcw_ws`).
From Windows, the Ubuntu files are visible at `\\wsl.localhost\Ubuntu\home\damilare\`.

### 3.2 On the Ubuntu side (the real project)

```
/home/damilare/                       (= ~)
├── hcw_ws/                           THE PROJECT. A Git clone of the GitHub repository.
│   ├── README.md                     entry point with a "start here" table
│   ├── docs/
│   │   ├── 00_Quick_Start_Run_Workflow.md       start-of-session checklist and roadmap table
│   │   ├── 01_Environment_Setup.md              how the machine was set up (GPU fix, installs, versions)
│   │   ├── 02_Atlas_Autonomy_Evaluation.md      why Atlas-Autonomy was rejected
│   │   ├── 03_OpenRMF_Clinic_World_Evaluation.md    clinic world evaluation (still being completed)
│   │   ├── 04_Clinic_Simulation_Bringup.md      how our clinic + TurtleBot simulation runs, with results
│   │   └── STRUCTURE.md                         short folder guide and Git rules
│   ├── scripts/
│   │   ├── env.sh                    source in EVERY terminal (ROS + clinic assets + our workspace)
│   │   └── clean_sims.sh             stop all simulations before starting a new one
│   ├── src/                          our ROS 2 packages (one folder = one job)
│   │   ├── hcw_bringup/              launch files (launch/sim_clinic.launch.py)
│   │   └── hcw_world/                clinic world builder (hcw_world/world_builder.py), models/ and worlds/ for later
│   ├── build/  install/  log/        generated by colcon; NOT in Git
│
├── eval/                             evaluation workspaces, kept outside the project on purpose
│   ├── rmf_ws/                       Open-RMF demos (clinic world source and assets). REQUIRED by our launch.
│   └── atlas_ws/                     failed Atlas-Autonomy attempt. Not used. Safe to delete.
│
├── .gazebo/models/                   286 MB of furniture and people models downloaded by the rmf_ws build
├── .gz/fuel/                         153 MB Gazebo Fuel model cache
└── wlr/, text.txt                    unrelated leftovers
```

### 3.3 How the pieces depend on each other

```
/opt/ros/jazzy   (apt: ROS, Gazebo, Nav2, TurtleBot 4 packages)
        ▲
~/eval/rmf_ws    (clinic.world, building meshes, asset models)      ← never edited by us
        ▲
~/hcw_ws/src/hcw_world      reads clinic.world, patches a COPY → /tmp/hcw_clinic.sdf
        ▲
~/hcw_ws/src/hcw_bringup    starts Gazebo server + GUI, robot_state_publisher, TurtleBot spawn + bridges, RViz
```
`source ~/hcw_ws/scripts/env.sh` chains all of this in the right order. If `rmf_ws` is missing, the
simulation cannot start (see section 5.3 for the rebuild).

## 4. What is running and how it works

### 4.1 Start command

```bash
cd ~/hcw_ws
source scripts/env.sh
scripts/clean_sims.sh                                  # stop leftovers
ros2 launch hcw_bringup sim_clinic.launch.py           # Gazebo + RViz open on the Windows desktop
```
Options: `profile:=building|floor1|full`, `headless:=True`, `x_pose:= y_pose:= yaw:=`.

### 4.2 What the launch does, step by step

1. `world_builder.py` copies the Open-RMF `clinic.world` and patches the copy:
   adds the Sensors and IMU systems (otherwise camera and LiDAR give no data), removes the Open-RMF
   door/lift plugins and demo robots, marks models static, and keeps only the parts of the chosen `profile`.
2. Starts the Gazebo server on that world, and the Gazebo window (unless `headless`).
3. Starts `robot_state_publisher` with the TurtleBot 4 description.
4. Spawns the TurtleBot 4 at (8.0, -31.7), the "L1_sub_waiting_area_1" parking spot, and starts the
   ROS to Gazebo bridges.
5. Starts RViz with the TurtleBot configuration.

### 4.3 What you see and what the robot offers

- **The clinic has 2 floors (L1 and L2) connected by lifts.** We load **only the ground floor (L1) shell**
  (`profile=building`): walls, rooms and corridors, with no beds, chairs, people or equipment. That is why it looks plain.
- Robot topics: `/cmd_vel` (drive input), `/odom`, `/scan` (2D LiDAR, about 10 Hz), `/imu`,
  `/rgbd_camera/image`, `/rgbd_camera/depth_image`, `/tf`, `/clock`.
- Verified 2026-10-24: real-time factor 1.0; robot drives (0.3 m/s for 6 s gave 0.95 m on `/odom`).

### 4.4 Why the hospital looks plain, and whether we can detail it

The full Open-RMF clinic has about 700 furniture and people models. With them loaded, the camera and
LiDAR rendering drops the simulation to 1 to 3 percent of real time, which is unusable (measured; the
world without a robot runs at full speed, so physics is not the cause). So the default world is the empty shell.

Yes, it can be detailed, as long as we add things **selectively and lightly**:
- Add only what the task needs: beds, trolleys, waste bins, the marked containers (AprilTags), a few obstacles.
- Prefer simple, low-polygon models. Each detailed model costs rendering time.
- Put our models in `hcw_world/models/`. Measure the real-time factor after each addition
  (`gz topic -e -t /stats -n 1 | grep real_time_factor`); stay above about 0.8.
- Beds and other furniture are a "later" item, as agreed.

## 5. How a teammate gets the same setup (Beni and David)

Each teammate has their own Windows laptop, so each sets up their own WSL Ubuntu copy of this machine.
You do **not** share Dami's machine; you share the GitHub repository and the same versions.

### 5.1 One-time setup per teammate
1. Follow `docs/01_Environment_Setup.md` (WSL2, Ubuntu 24.04, NVIDIA driver on Windows, GPU fix, ROS 2 Jazzy, Gazebo, Nav2).
   Check that `glxinfo -B | grep "OpenGL renderer"` says D3D12 and NVIDIA, not llvmpipe.
2. Pick your own `ROS_DOMAIN_ID` and add it to `~/.bashrc`. Use a different number from Dami's 11.
3. Clone the project:
   ```bash
   mkdir -p ~/hcw_ws && cd ~/hcw_ws
   git clone https://github.com/damilareadekeye/AUTONOMOUS-HEALTHCARE-WASTE-COLLECTION-ROBOT.git .
   ```
   (Dami must add Beni and David as collaborators on GitHub first.)
4. Build the clinic assets (about 5 minutes, section 5.3).
5. `cd ~/hcw_ws && source scripts/env.sh && colcon build --symlink-install`, then run section 4.1.

### 5.2 Daily routine
```bash
cd ~/hcw_ws && git pull
source scripts/env.sh
scripts/clean_sims.sh
```
Work on a branch (`git switch -c feature/<name>`), commit small, push, open a pull request. `main` must always build and run.

### 5.3 Clinic assets build (once per machine)
```bash
mkdir -p ~/eval/rmf_ws/src && cd ~/eval/rmf_ws/src
git clone -b jazzy https://github.com/open-rmf/rmf_demos.git
cd ~/eval/rmf_ws
sudo apt update && sudo apt install -y ros-jazzy-rmf-dev
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --continue-on-error
```
Models download into `~/.gazebo/models`.

### 5.4 Proposed split of work (edit if you disagree)

| Person | Area | Packages |
|---|---|---|
| Dami | Perception: camera, AprilTag, verification rule (matches the camera plan PDF) | `hcw_perception` |
| Beni | Navigation: SLAM map, Nav2 settings, named locations | `hcw_navigation` |
| David | Task manager: Simple Commander state machine, tests and result tables | `hcw_task` |
| Everyone | World and simulation (`hcw_world`, `hcw_bringup`), documentation | shared |

## 6. Where the project stands against the schedule

Schedule source: `Baseline_Implementation_Timeline.pdf` (submitted Oct 12). Target: **Sunday Nov 8**.
Review meeting: week of **Nov 9**. Today: **Saturday Oct 24**, the second-to-last day of Week 2.
The progress update to the mentor is due **Oct 25**.

### Week 1 (Oct 12 to 18): environment and evaluations. Status: DONE, one decision still provisional

| Planned | State |
|---|---|
| Install Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic, Nav2; record versions | Done (doc 01) |
| Run the official Nav2 simulation | Done, passed (RTF about 100 %) |
| Build and run Atlas-Autonomy | Done: attempted twice, does not build; rejected (doc 02) |
| Test whether the Open-RMF Clinic World can be reused | Mostly done: builds, launches, and our own launch runs it with a TurtleBot at full speed. Only the L1 shell is practical. |
| Decision: Clinic World or adapted office world | **Provisional: Clinic ground floor shell.** Final confirmation needs the Nav2 test in Week 2. |

### Week 2 (Oct 19 to 25): world, map, locations, camera, AprilTag. Status: about 25 % done, BEHIND

| Planned | State |
|---|---|
| Finalise the hospital-like world | Partly: shell runs; no obstacles, containers or markers yet |
| Build the map with SLAM Toolbox | **Not started** |
| Define named locations (collection points A, B, C, storage, home) | **Not started** |
| Add a camera to the robot | Done (TurtleBot 4 RGB-D camera publishes `/rgbd_camera/image`) |
| AprilTag-marked container models | **Not started** |
| `apriltag_ros` detection, tag IDs published in ROS 2 | **Not started** (package not yet installed) |
| Progress update to mentor (Oct 25) | **Due tomorrow.** Can honestly report: environment, evaluations and clinic world with robot done; map and tags next. |

Checkpoint "Robot navigates to named locations; tag IDs detected": **not reached**.

### Weeks 3 and 4: not started
Task manager, verification rule, attach/release, wrong-container handling (Week 3); repeated tests and documentation (Week 4).

### Overall
Roughly **1.3 of 4 weeks of work done**, with 15 days left to Nov 8. It is recoverable if the map,
locations and tags are done in the next 4 to 5 days. The schedule document itself allows 3 to 5 weeks, so
the realistic range ends around Nov 22. Tell the mentor early if the dates will move.

## 7. Roadmap: what is left (in order)

Dates are targets. "Owner" follows the proposed split in 5.4.

| # | Task | Output / done when | Owner | Target |
|---|---|---|---|---|
| 1 | Send the Week 2 progress update | Email with honest status | Dami | Oct 25 |
| 2 | Confirm clinic L1 works with Nav2: drive around, check corridors and doors are passable for the robot | Decision written in doc 03: "Clinic L1 shell" or office world | Beni | Oct 26 |
| 3 | Build the map with SLAM Toolbox and save it | `hcw_navigation/maps/clinic.yaml` + `.pgm` | Beni | Oct 27 |
| 4 | Run Nav2 on the saved map: localise, plan, avoid obstacles | Robot reaches RViz goals reliably | Beni | Oct 28 |
| 5 | Define named locations: collection points A, B, C, storage, home | `locations.yaml`; "go to A" works from a script | Beni | Oct 28 |
| 6 | Install `apriltag_ros`; create container models with tags 11, 12, 13 (Dami's plan) | Tag IDs on a ROS topic when the robot faces a container | Dami | Oct 29 |
| 7 | Add lightweight clinic details: containers at A, B, C, bins, a few obstacles, optional beds | Real-time factor still above 0.8 | Dami / everyone | Oct 30 |
| 8 | Verification node: expected tag seen for N consecutive frames, then `VERIFIED` | Wrong or missing tag never gives `VERIFIED` | Dami | Oct 31 |
| 9 | Task manager: Nav2 Simple Commander plus state machine (idle, go to A, verify, attach, go to storage, release, report, return home) | One full run end to end in simulation | David | Nov 1 (first run) |
| 10 | Simulated attach and release (simplest reliable method, documented) | Container moves with the robot, stays at storage | David | Nov 2 |
| 11 | Failure handling: wrong container, missing container, blocked path (wait, retry, report) | Each case ends safely | David | Nov 3 |
| 12 | Repeated tests: 20 to 30 runs, all collection points, wrong-container and obstacle cases | `docs/results/` table: success rate, time per stage, failures and causes | David + all | Nov 4 to 6 |
| 13 | Final documentation and README; check another teammate can reproduce from scratch | Docs complete | Everyone | Nov 7 |
| 14 | Buffer, then review meeting | Working baseline presented | Everyone | Nov 8, meeting week of Nov 9 |

Optional, only after the baseline works: YOLO detector experiment (synthetic dataset plan is in the camera PDF),
more detailed hospital, a second floor via the lifts, Open-RMF fleet features.

### Risks to watch
- **Simulation speed:** adding models can drop the real-time factor. Measure after each addition.
- **Attach/release in Gazebo can be unreliable:** start with the simplest method (for example moving the container model with the robot) and document it.
- **Team machines:** each teammate must reach the same working setup; check `glxinfo` early.
- **Time:** coursework and exams; keep the weekly check-in.

## 8. Quick reference

| I want to... | Command / file |
|---|---|
| Open a terminal in the project | Windows Start menu, Ubuntu, then `cd ~/hcw_ws` |
| Start the simulation | `source scripts/env.sh && scripts/clean_sims.sh && ros2 launch hcw_bringup sim_clinic.launch.py` |
| Stop everything | `scripts/clean_sims.sh` (or Ctrl+C in the launch terminal) |
| Drive the robot by keyboard | `ros2 run teleop_twist_keyboard teleop_twist_keyboard` (install: `sudo apt install ros-jazzy-teleop-twist-keyboard`) |
| Check simulation speed | `gz topic -e -t /stats -n 1 \| grep real_time_factor` |
| See robot topics | `ros2 topic list` |
| Save my work | `git add -A && git commit -m "message" && git push` |
| Re-check the GPU | `glxinfo -B \| grep "OpenGL renderer"` (must say D3D12 NVIDIA) |
| Restart WSL fully | PowerShell: `wsl --shutdown`, then reopen Ubuntu |

Troubleshooting: `docs/01_Environment_Setup.md` section 7 and `docs/04_Clinic_Simulation_Bringup.md` ("Findings and fixes").
