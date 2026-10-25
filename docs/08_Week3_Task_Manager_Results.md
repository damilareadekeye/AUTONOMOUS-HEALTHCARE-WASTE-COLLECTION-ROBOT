# 08 — Week 3: Task Manager, Verification and Magnet (results)

Last updated: 2026-10-25. Design: `07_Task_Manager_Design.md`. Reference machine only.

## 1. What was built

| Part | Package / file | What it does |
|---|---|---|
| Verifier | `hcw_perception/verifier.py` | Expected tag seen alone in 5 consecutive detection messages = VERIFIED. Publishes `/perception/target_status` |
| Magnet (simulated) | `hcw_task/magnet.py` | Attach: the container follows the robot (carried above the LiDAR plane). Release: put down at the storage drop point. Moves the model with Gazebo's `set_pose` service, bridged to ROS |
| Task manager | `hcw_task/task_manager.py` | State machine: IDLE, NAVIGATE_TO_POINT, VERIFY, ATTACH, NAVIGATE_TO_STORAGE, RELEASE, REPORT, RETURN_HOME. Failures end in FAILED, put the container back, return home |
| Request tool | `hcw_task/request.py` | `ros2 run hcw_task request A` prints every state change |
| Log | `~/hcw_ws/results/runs.csv` | One row per task (columns of the run-log template). Not committed |

The magnet is a simulation of a magnetic latch: Gazebo has no gripper here, so the container model is moved with the robot.
Nav2 alone moves the robot; the task manager and verifier never publish velocity commands.

## 2. Run it

```bash
# terminal 1
scripts/clean_sims.sh && source scripts/env.sh
ros2 launch hcw_bringup sim_clinic.launch.py
# terminal 2 (wait about 45 s, then)  navigation, perception, task manager
ros2 launch hcw_navigation navigation.launch.py
# terminal 3
ros2 launch hcw_perception apriltag.launch.py
# terminal 4
ros2 launch hcw_task task.launch.py
# terminal 5: ask for collections
ros2 run hcw_task request A            # or B, C, or several: request A B C
```
Each terminal needs `source ~/hcw_ws/scripts/env.sh` first. The robot must start at home.

## 3. Results (2026-10-25, reference machine, Gazebo window closed, real-time factor 1.0)

Single runs, not yet a statistical test. Times are simulated seconds.

| # | Scenario | Result | Navigate to point | Verify | Transport to storage | Cause |
|---|---|---|---|---|---|---|
| 1 | Normal, point A | COMPLETED | 38.4 s | 0.5 s | 46.0 s | |
| 2 | Normal, point B | COMPLETED | 25.0 s | 0.5 s | 61.6 s | |
| 3 | Normal, point C | COMPLETED | 12.9 s | 0.5 s | 76.1 s | |
| 4 | Missing container at A (container 11 moved away) | FAILED, as designed | 39.8 s | 39.0 s (3 attempts) | | no container tag detected (expected 11) |
| 5 | Wrong container at A (container 13 stands where 11 should be) | FAILED, as designed | 38.5 s | 39.0 s (3 attempts) | | wrong container (tag [13] seen, expected 11) |
| 6 | Normal, point A, after the two failures | COMPLETED | 38.0 s | 0.5 s | 45.2 s | |
| 7 | Invalid request "Z" | REJECTED | | | | invalid request (use A, B or C) |

After each task the task manager returned to IDLE (a failed task puts the container back and drives home first). The log
does not record whether the home leg itself succeeded; each following task started from there and behaved as expected.

## 4. What this does not show yet

- **Repetition:** 6 tasks in this session (4 completed, 2 failed as designed) plus one invalid request. The plan needs 20 to 30
  runs for a success rate; that is Week 4.
- **Verification time 0.5 s** is the minimum (5 detection messages at about 10 per second). It is not a measure of difficulty.
- **Tested later the same day** (section 4c): obstacle with a gap, blocked corridor, request while busy.
  **Still not shown in the simulation:** an unstable tag (the rule is unit-tested instead); Nav2 failing mid-route with the container attached.
- **Magnet realism:** the container floats above the robot while carried and is dropped at the storage bay (x 30.9, y -12.4).
  The robot stands 1.8 m from the container when it attaches ("magnet range" 2.5 m), because the doorways are blocked on the map.
- **Wrong-container test** was set up by moving container 13 to A's place, not by the decoy model (tag 14).

## 4b. Automated batch check (2026-10-25, `scripts/start_stack.sh` then `scripts/run_batch.sh 1 --with-failures`)

The first attempt was invalid and was discarded: `clean_sims.sh` did not stop the task manager and magnet of an earlier run, so two
copies answered the same request. The script now stops them. Clean rerun, all started by the scripts, no manual steps:

| Task | Case | Result | Cause reported |
|---|---|---|---|
| 7 | Normal, A | COMPLETED (navigate 38.6 s, verify 0.5 s, transport 45.4 s) | |
| 8 | Missing container, A | FAILED as designed | no container tag detected (expected 11) |
| 9 | Wrong container, A (tag 12 in its place) | FAILED as designed | wrong container (tag [12] seen, expected 11) |
| 10 | Missing container, B | FAILED as designed | no container tag detected (expected 12) |
| 11 | Wrong container, B (tag 13) | FAILED as designed | wrong container (tag [13] seen, expected 12) |
| 12 | Missing container, C | FAILED as designed | no container tag detected (expected 13) |
| 13 | Wrong container, C (tag 11) | FAILED as designed | wrong container (tag [11] seen, expected 13) |

Whole batch about 15 minutes (a normal task about 3.2 minutes, a fault case about 1.5 to 2 minutes). Runs 1 to 6 in `runs.csv` are from the
first session today. For the 20 to 30 runs use `scripts/run_batch.sh 18 --with-failures` (about 1.5 hours, unattended).

## 4c. Obstacle, busy request and unstable tag (2026-10-25, stack running, started by hand with `scenario` notes in the CSV)

| Task | Case | Result | Detail |
|---|---|---|---|
| 14 | Request B while the task for A was running | A COMPLETED; B REJECTED | "a task is already running"; the first task was not disturbed |
| 15 | 0.6 m box in the corridor (a gap remains), request A | COMPLETED | navigate 42.8 s (about 39 s without the box): Nav2 went around it |
| 16 | Corridor blocked completely (3.0 m box wall), request A | FAILED as designed | "navigation to the collection point failed" after 64 s; task manager returned to IDLE |
| 17 | Normal A after the blockage was removed | COMPLETED | recovery works |
| 18, 19 | Container 11 made to disappear and reappear (about 0.8 s and about 1.2 s cycles) while the robot verified | COMPLETED on attempt 1, verify 2.0 s | **Inconclusive**: the move commands are slow, so the tag was probably visible long enough each time. It does not show that the rule rejects an unstable tag |

The unstable-tag rule is instead tested directly: `src/hcw_perception/test/test_verifier_rule.py` (8 tests, all pass).
Run: `cd ~/hcw_ws && source scripts/env.sh && python3 -m unittest src/hcw_perception/test/test_verifier_rule.py -v`.
It checks: 5 consecutive frames verify; 4 frames then a gap, repeated, never verifies; another tag in view blocks it; the wrong tag
alone does not verify; nothing in view does not verify; changing the expected tag resets the count; not looking never verifies; the JSON status matches.

Still not tested in the simulation: a blocked corridor on the way to storage with the container attached; Nav2 failing during the return home;
two requests queued back to back (a request while busy is rejected, not queued).

## 5. Controls for testing (reference machine)

| Control | Command |
|---|---|
| Keep the containers where you put them (missing or wrong container test) | `ros2 param set /task_manager reset_container false` (set it back to `true` afterwards, then `ros2 topic pub --once /magnet/command std_msgs/msg/String "{data: 'reset:all'}"`) |
| Label the next CSV rows | `ros2 param set /task_manager wrong_container true`, `obstacle true`, `notes "text"` |
| Move a container | `ros2 service call /world/sim_world/set_pose ros_gz_interfaces/srv/SetEntityPose "{entity: {name: 'hcw_container_13', type: 2}, pose: {position: {x: 15.4, y: -18.6, z: 0.0}, orientation: {z: 1.0, w: 0.0}}}"` |
| Watch status | `ros2 topic echo /hcw/task_status` and `/perception/target_status` |
