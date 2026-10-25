# 07 — Task Manager Design (Week 3)

Last updated: 2026-10-25. Status: design agreed with the team; implementation in progress on the reference machine.

## 1. Goal

Receive a task ("collect the container at point A"), drive to the collection point, verify the container with the
camera, "attach" it with a magnet, drive to storage, release it, report completion and return home.
Wrong or unstable detections lead to wait, retry or a reported failure, never to unsafe motion.

## 2. Decisions (agreed 2026-10-25)

| Topic | Decision | Reason |
|---|---|---|
| Attach / release | **Simulated magnet**: when the tag is verified, the container model follows the robot; at storage it is put down. In the demo it is described as a magnetic latch. | A physical grip in Gazebo is slow to build and unreliable on demo day (risk table in the timeline) |
| Navigation | Nav2 only (via the Nav2 Simple Commander). The task manager never publishes velocity commands | Design rule from the mentor |
| Perception | `apriltag_ros` publishes detections; the verifier node decides VERIFIED; it never publishes motor commands | Design rule |
| Verification rule | Expected tag seen in **5 consecutive** detection messages, and **no other tag** in view | Single noisy detections must not trigger pickup |
| Failure policy | Wrong or no tag: wait 3 s and retry up to 3 times, then report FAILED and return home | "Wait, retry or report failure" |

## 3. Components

```
 /hcw/task_request ──► task_manager ──► Nav2 (NavigateToPose)
 (String: "A")            │   │
                          │   ├─ /perception/expected_tag (Int32) ──► verifier ◄── /detections (apriltag_ros)
                          │   │                                          │
                          │   ◄──────────── /perception/target_status (String, JSON) ─┘
                          │   └─ /magnet/command (String) ──► magnet node ──► Gazebo set_pose (container model)
                          └──► /hcw/task_status (String, JSON)
```

| Node | Package | Job |
|---|---|---|
| `task_manager` | `hcw_task` | State machine below; logs one CSV row per task |
| `verifier` | `hcw_perception` | Applies the verification rule, publishes `/perception/target_status` |
| `magnet` | `hcw_task` | Moves the container model with the robot while attached, puts it down on release |

## 4. State machine

`IDLE` → `NAVIGATE_TO_POINT` → `VERIFY` → `ATTACH` → `NAVIGATE_TO_STORAGE` → `RELEASE` → `REPORT` → `RETURN_HOME` → `IDLE`

| State | What happens | Leaves when |
|---|---|---|
| IDLE | Waits for `/hcw/task_request` ("A", "B" or "C") | A valid request arrives |
| NAVIGATE_TO_POINT | Nav2 goal to `collection_<X>` | Reached, or Nav2 fails (go to FAILED) |
| VERIFY | Sets the expected tag (A=11, B=12, C=13), waits up to 10 s for VERIFIED | VERIFIED, or timeout: retry (wait 3 s, up to 3 attempts), then FAILED |
| ATTACH | Magnet latches the container | Magnet reports attached |
| NAVIGATE_TO_STORAGE | Nav2 goal to `storage` | Reached, or fails (FAILED) |
| RELEASE | Magnet puts the container down at storage | Magnet reports released |
| REPORT | Publishes `COMPLETED` with timings | Always |
| RETURN_HOME | Nav2 goal to `home` | Reached or failed (logged), then IDLE |
| FAILED | Publishes the failure cause, releases the magnet if attached, returns home | Then IDLE |

## 5. Interfaces (all `std_msgs`, JSON text where noted, no custom message package)

| Topic | Type | Content |
|---|---|---|
| `/hcw/task_request` | String | `A`, `B` or `C` |
| `/hcw/task_status` | String (JSON) | `{task_id, state, point, result (RUNNING/COMPLETED/FAILED), cause, t_navigate, t_verify, t_transport}` |
| `/perception/expected_tag` | Int32 | Tag id the verifier should look for; 0 = idle |
| `/perception/target_status` | String (JSON) | `{expected_id, detected_ids, detected, verified, consecutive, stamp}` |
| `/magnet/command` | String | `attach:<tag_id>` or `release:<x>,<y>,<yaw>` |
| `/magnet/status` | String | `attached:<tag_id>`, `released`, or `error:<text>` |

Places and tag ids come from `hcw_world/config/locations.yaml`; do not repeat them in code.

## 6. Logging

One CSV row per task in `~/hcw_ws/results/runs.csv` (not committed; copy to `docs/results/` after a test session)
with the columns of `docs/results/run_log_template.csv` (Beni's Task 2). That file feeds the Week 4 success-rate table.

## 7. Test scenarios the design must pass (David's Task 7 turns this into a plan)

Normal A, B, C; wrong container in front of the robot (tag 14); no container (container removed); unstable tag
(covered or blocked briefly); obstacle in the corridor; Nav2 failure; task request while busy; invalid request.
