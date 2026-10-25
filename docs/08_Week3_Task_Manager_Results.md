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
- **Not tested:** an obstacle in the corridor; a tag that is covered briefly (unstable detection); a task request while
  busy (code path exists, no test yet); two tasks in a row without the robot first returning home; Nav2 failing mid-route.
- **Magnet realism:** the container floats above the robot while carried and is dropped at the storage bay (x 30.9, y -12.4).
  The robot stands 1.8 m from the container when it attaches ("magnet range" 2.5 m), because the doorways are blocked on the map.
- **Wrong-container test** was set up by moving container 13 to A's place, not by the decoy model (tag 14).

## 5. Controls for testing (reference machine)

| Control | Command |
|---|---|
| Keep the containers where you put them (missing or wrong container test) | `ros2 param set /task_manager reset_container false` (set it back to `true` afterwards, then `ros2 topic pub --once /magnet/command std_msgs/msg/String "{data: 'reset:all'}"`) |
| Label the next CSV rows | `ros2 param set /task_manager wrong_container true`, `obstacle true`, `notes "text"` |
| Move a container | `ros2 service call /world/sim_world/set_pose ros_gz_interfaces/srv/SetEntityPose "{entity: {name: 'hcw_container_13', type: 2}, pose: {position: {x: 15.4, y: -18.6, z: 0.0}, orientation: {z: 1.0, w: 0.0}}}"` |
| Watch status | `ros2 topic echo /hcw/task_status` and `/perception/target_status` |
