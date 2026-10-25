# Autonomous Healthcare-Waste Collection Robot

IEEE Rwanda Mentorship Program. A simulated indoor robot that receives a collection task, drives to a
collection point, verifies the container with a camera (AprilTag), carries it to the storage point,
releases it, reports completion and returns home.

Stack: Ubuntu 24.04 (WSL2) · ROS 2 Jazzy · Gazebo Harmonic · Nav2 · AprilTag. No training data needed.

## Start here

| I want to... | Read |
|---|---|
| Run the simulation today | [docs/00_Quick_Start_Run_Workflow.md](docs/00_Quick_Start_Run_Workflow.md) |
| **Contributing (Beni, David): tasks and rules** | [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) (AI agents: [CLAUDE.md](CLAUDE.md)) |
| Run the clinic + TurtleBot simulation | [docs/04_Clinic_Simulation_Bringup.md](docs/04_Clinic_Simulation_Bringup.md) |
| Map, named places, Nav2, AprilTag results | [docs/05_Mapping_Navigation_Perception.md](docs/05_Mapping_Navigation_Perception.md) |
| Week 2 progress update (draft for the mentor) | [docs/06_Progress_Update_Week2.md](docs/06_Progress_Update_Week2.md) |
| Week 3 design: task manager, verifier, magnet | [docs/07_Task_Manager_Design.md](docs/07_Task_Manager_Design.md) |
| Week 3 results and how to run a task | [docs/08_Week3_Task_Manager_Results.md](docs/08_Week3_Task_Manager_Results.md) |
| **All commands in one file** | [docs/COMMANDS.md](docs/COMMANDS.md) |
| Team decisions (what we postponed and why) | [docs/DECISIONS.md](docs/DECISIONS.md) |
| **Full picture of the project, the machine and the roadmap** | [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) |
| Understand the folders and who owns what | [docs/STRUCTURE.md](docs/STRUCTURE.md) |
| Install everything on a new machine | [docs/01_Environment_Setup.md](docs/01_Environment_Setup.md) |
| See why Atlas-Autonomy was dropped | [docs/02_Atlas_Autonomy_Evaluation.md](docs/02_Atlas_Autonomy_Evaluation.md) |
| See the clinic world evaluation | [docs/03_OpenRMF_Clinic_World_Evaluation.md](docs/03_OpenRMF_Clinic_World_Evaluation.md) |

## Run the clinic simulation

```bash
cd ~/hcw_ws && git pull
colcon build --symlink-install            # first time, and after changing packages
source scripts/env.sh                     # in EVERY new terminal
ros2 launch hcw_bringup sim_clinic.launch.py
```
Needs the one-time clinic assets build: see "Clinic assets" in [docs/STRUCTURE.md](docs/STRUCTURE.md).
Before starting another simulation: `scripts/clean_sims.sh`.

## Layout

```
hcw_ws/
├── README.md              you are here
├── docs/                  setup, evaluations, results, structure guide
├── scripts/               env.sh (every terminal), clean_sims.sh
└── src/                   ROS 2 packages (one folder = one job)
    ├── hcw_bringup/       launch files: start the simulation (and later the full system)
    ├── hcw_world/         clinic world builder (+ our own models later, e.g. AprilTag containers)
    ├── hcw_navigation/    saved map, Nav2 and SLAM Toolbox settings, go_to command
    ├── hcw_perception/    AprilTag detection (verification rule still to do)
    └── hcw_task/          task manager (state machine) and simulated magnet
```
