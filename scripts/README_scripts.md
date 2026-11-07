# scripts/

| Script | Use |
|---|---|
| `env.sh` | `source scripts/env.sh` in every terminal (ROS, clinic assets, this workspace, `ROS_DOMAIN_ID` 11) |
| `clean_sims.sh` | Stop everything, including leftover processes. Run before every new start |
| `start_stack.sh [gui] [props]` | Start the simulation, Nav2, tag detection and the task manager. `gui` opens the Gazebo window, `props` adds the hospital-room props |
| `run_batch.sh N [--with-failures]` | Unattended repeated runs (N normal tasks, optionally the 6 fault cases) |
| `summarize_runs.py [--from-run N]` | Success rate, times and failure causes from `~/hcw_ws/results/runs.csv` |
| `check_speed.sh` | Simulation speed in percent of real time, with advice (run before a demo) |
| `demo_camera.sh top\|west\|follow\|robot` | Move the Gazebo window's camera |
| `demo_fault.sh missing\|wrong A\|B\|C`, `demo_fault.sh reset` | Stage a missing or wrong container for a demo |
| `test_all_places.sh` | Drive to every named place with tag checks (about 6 minutes) |

If a script says "Permission denied" (a file edited on Windows can lose its executable flag), run it with `bash scripts/<name>`.
