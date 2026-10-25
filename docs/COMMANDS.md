# All commands in one file

Run these in an **Ubuntu terminal on Dami's machine** (the only machine that runs the simulation).
Last updated: 2026-10-25. Every terminal starts with `cd ~/hcw_ws && source scripts/env.sh`.

## 1. Daily start

| Step | Command | What it does |
|---|---|---|
| 1 | `cd ~/hcw_ws && git pull` | Get the latest code |
| 2 | `scripts/start_stack.sh` | Stops leftovers, builds, starts the simulation, Nav2, tag detection and the task manager. Prints `STACK READY` after about 1.5 minutes |
| 2b | `scripts/start_stack.sh gui` | Same, with the Gazebo window (about 10 times slower; for showing people) |
| 3 | `ros2 run hcw_task request A` | Do a whole collection from point A (also `B`, `C`, or `request A B C`) |
| end | `scripts/clean_sims.sh` | Stop everything |

The robot must be at the Home spot when the stack starts. After driving it by hand, restart with step 2.

## 2. Watch the simulation

| Want | Command |
|---|---|
| Gazebo window (while the stack runs) | `gz sim -g` (slows the simulation; close it when done) |
| RViz | start the simulation with `ros2 launch hcw_bringup sim_clinic.launch.py rviz:=True` instead of step 2 |
| Task states | `ros2 topic echo /hcw/task_status` |
| What the camera sees (tag ids) | `ros2 run hcw_perception tag_monitor` (prints changes) or `ros2 topic echo /perception/target_status` |
| Simulation speed (should be about 1.0) | `gz topic -e -t /stats -n 1 \| grep real_time_factor` |

## 3. Drive the robot by hand (stack not needed, only the simulation)

```bash
ros2 launch hcw_bringup sim_clinic.launch.py gui:=True       # terminal 1
ros2 run hcw_bringup teleop_arrows                            # terminal 2: arrow keys, Space = stop, q = quit
```

## 4. The 20 to 30 repeated runs (Week 4), unattended

```bash
scripts/start_stack.sh
scripts/run_batch.sh 18 --with-failures        # 18 normal tasks + 6 fault cases, about 1.5 hours
python3 scripts/summarize_runs.py              # success rate, times, failure causes (all runs so far)
```
Raw rows: `~/hcw_ws/results/runs.csv` (not in Git; copy it into `docs/results/` after a session).
You can leave it running; it needs no AI and no keyboard.

## 5. Single tests

| Test | Commands |
|---|---|
| Go to a named place only (no task) | `ros2 run hcw_navigation go_to collection_A storage home` |
| Missing container | `ros2 param set /task_manager reset_container false`, move the container away (see `08_Week3_Task_Manager_Results.md`, section 5), `ros2 run hcw_task request A`; afterwards `ros2 param set /task_manager reset_container true` |
| Check the whole map and places | `scripts/test_all_places.sh` (about 6 minutes) |

## 6. Save work

```bash
git status
git add <files>
git commit -m "What changed"
git push                       # contributors from other laptops push a branch instead, see CONTRIBUTING.md
```

## 7. When something is wrong

| Symptom | Fix |
|---|---|
| `start_stack.sh` says Nav2 did not localise | `scripts/clean_sims.sh` then run it again; check that nothing else is running (`ps -eo args \| grep -c "lib/nav2_"` should be 0 after cleaning) |
| A command hangs and prints nothing | Press Ctrl+C, `scripts/clean_sims.sh`, start again. Never start a second copy on top of a running one |
| Robot does not move | Is the stack ready? Is this terminal sourced with `scripts/env.sh` (same `ROS_DOMAIN_ID` 11)? |
| `request` says the task manager is not running | Run `scripts/start_stack.sh` first |
| Simulation very slow | Close the Gazebo window and RViz; check `real_time_factor` |
| Logs | `/tmp/hcw_launch.log`, `/tmp/hcw_nav.log`, `/tmp/hcw_tags.log`, `/tmp/hcw_task.log` |
