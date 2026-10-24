# 03 — Open-RMF Clinic World Evaluation

Autonomous Healthcare-Waste Collection Robot — IEEE Rwanda Mentorship Program
Last updated: 2026-10-19

Mentor's instruction: test whether the Open-RMF Clinic World can be reused; if that is too complex,
adapt a simple office world into a hospital-like environment.

- Source: https://github.com/open-rmf/rmf_demos (branch `jazzy`) — officially tested on Ubuntu 24.04 + ROS 2 Jazzy + Gazebo Harmonic
- The Clinic World has two levels (L1, L2) and two lifts. Only the ground floor (L1) is relevant to our robot.
- Evaluated in a separate workspace (`~/eval/rmf_ws`) so it cannot affect the project workspace (`~/hcw_ws`).

## Step 1 — Build and launch (2026-10-19)

Open a **new terminal** first (do not reuse a terminal that sourced another evaluation workspace).

```bash
mkdir -p ~/eval/rmf_ws/src && cd ~/eval/rmf_ws/src
git clone -b jazzy https://github.com/open-rmf/rmf_demos.git

cd ~/eval/rmf_ws
sudo apt update && sudo apt install -y ros-jazzy-rmf-dev
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --continue-on-error 2>&1 | tee build.log
grep -E "Finished|Failed|Aborted|Summary" build.log | tail -20

source install/setup.bash
ros2 launch rmf_demos_gz clinic.launch.xml
```

### Build result: PASSED

| Item | Result |
|---|---|
| `ros-jazzy-rmf-dev` (58 Open-RMF packages from apt) | Installed |
| rosdep extra dependencies (paho-mqtt, flask-socketio, fastapi, pydantic, uvicorn — all via apt) | Installed |
| rmf_demos_assets, rmf_demos_fleet_adapter, rmf_demos_tasks, rmf_demos_bridges, rmf_demos_maps, rmf_demos, rmf_demos_gz | All 7 built (5 min 20 s) |
| `rmf_demos_maps` stderr | Informational only: it generates each world file (airport, battle_royale, campus, clinic, hotel, office, triple_H) and downloads its 3D models. Not an error. |

### Launch result

All Open-RMF processes started (traffic schedule, building map server, door/lift supervisors, task
dispatcher, two fleet managers/adapters, Gazebo, ROS–Gazebo bridge, RViz).

| Check | Result |
|---|---|
| RViz shows the clinic L1 floor plan ("Clinic A & B layout plan") with the Open-RMF navigation graph (blue lanes) at ~30 fps | Pass |
| Gazebo opens the clinic world (3D) | _To be confirmed (screenshot)_ |

Observation: the L1 floor plan contains wide corridors, ~20 consultation rooms, treatment rooms,
waiting areas, a STORE room and an E-TROLLEY room — a good match for collection points (rooms) and a
storage point (STORE / E-TROLLEY) in our waste-collection task.
| Real-time factor | _To be recorded_ |
| Errors in launch output | _To be checked_ |

## Step 2 — Can our robot use the clinic ground floor with Nav2?

_Pending._

## Decision

_Pending: reuse Clinic World (L1) or adapt an office world._
