# Test Plan — Repeated Simulation Runs (Week 4)

Based on `docs/07_Task_Manager_Design.md`, section 4 (state machine) and section 7 (test
scenarios). This plan does not contain any results; numbers are filled in only from real runs,
using `docs/results/run_log_template.csv`.

## How to read this table

- **Set up**: how to produce the scenario in simulation, in words. Items marked "(check)" use a
  mechanism not fully documented yet and need confirming on the reference machine before the
  run.
- **Expected states**: the state-machine path from `IDLE` the task should take, per doc 07
  section 4.
- **Expected result**: `COMPLETED` or `FAILED`, and the failure cause in words (the exact
  `cause` string used in `/hcw/task_status` should be confirmed against the real implementation;
  `(check)` marks where the wording here is a description, not a guaranteed exact string).
- **Pass rule**: what must be true for the run to count as a pass.

## Test cases

| ID | Scenario | Set up | Expected states | Expected result | Pass rule |
|---|---|---|---|---|---|
| TC01 | Normal task, point A | `ros2 run hcw_task request A` with the simulation, navigation, apriltag and task launches running as normal, correct tag (11) in place at A | IDLE → NAVIGATE_TO_POINT → VERIFY → ATTACH → NAVIGATE_TO_STORAGE → RELEASE → REPORT → RETURN_HOME → IDLE | COMPLETED | Robot reaches A, tag 11 verified, container moves with robot to storage, robot returns home, final state IDLE |
| TC02 | Normal task, point B | Same as TC01, `request B`, tag 12 in place at B | Same full sequence | COMPLETED | Same as TC01, for B / tag 12 |
| TC03 | Normal task, point C | Same as TC01, `request C`, tag 13 in place at C | Same full sequence | COMPLETED | Same as TC01, for C / tag 13 |
| TC04 | Wrong container at a collection point | (check) Launch with `decoy:=True` on `sim_clinic.launch.py` and arrange for tag 14 to be the tag seen at the collection point instead of the correct tag; confirm exact method with reference machine, since tag 14's documented default position is separate from A/B/C. Label the run with `wrong_container:=true` on `task.launch.py` for the CSV | IDLE → NAVIGATE_TO_POINT → VERIFY (fails: wrong tag seen, not the expected one) → wait 3 s, retry, up to 3 attempts → FAILED → RETURN_HOME → IDLE | FAILED, cause: wrong container / expected tag not verified (check exact cause string) | Task never reaches ATTACH; robot ends back at home; magnet never reports attached |
| TC05 | Wrong container at a different collection point | Same as TC04, repeated at a second collection point for coverage | Same as TC04 | FAILED, same cause type as TC04 | Same as TC04 |
| TC06 | Missing container at a collection point | `ros2 param set /task_manager reset_container false` before the run, with the container removed/not reset at the collection point (per the comment in `task.launch.py`) | IDLE → NAVIGATE_TO_POINT → VERIFY (no tag detected) → wait 3 s, retry, up to 3 attempts → FAILED → RETURN_HOME → IDLE | FAILED, cause: no container / tag not detected (check exact cause string) | Task never reaches ATTACH; robot ends back at home |
| TC07 | Missing container at a second collection point | Same as TC06, repeated at a different point for coverage | Same as TC06 | Same as TC06 | Same as TC06 |
| TC08 | Unstable tag that recovers | (check) Briefly block or cover the expected tag for less than 3 retry attempts, then let it be visible again, so the 5-consecutive-frames rule can still be satisfied before the 3-attempt limit is reached | IDLE → NAVIGATE_TO_POINT → VERIFY (one or more failed attempts, then succeeds within 3 retries) → ATTACH → ... → REPORT → RETURN_HOME → IDLE | COMPLETED | Task eventually reaches ATTACH and completes, despite at least one failed verification attempt being logged |
| TC09 | Unstable tag that never stabilises | (check) Keep the expected tag blocked/covered for the whole verification window, through all 3 retry attempts | IDLE → NAVIGATE_TO_POINT → VERIFY (fails every attempt) → FAILED → RETURN_HOME → IDLE | FAILED, cause: verification timeout / tag never stable (check exact cause string) | Task never reaches ATTACH; all 3 retry attempts are logged as failed |
| TC10 | Obstacle blocking the corridor to a collection point | (check) Place an obstacle in the corridor between home and a collection point so Nav2 cannot find or complete a path; label the run with `obstacle:=true` on `task.launch.py` for the CSV | IDLE → NAVIGATE_TO_POINT (Nav2 fails to reach the goal) → FAILED → RETURN_HOME (if possible) → IDLE | FAILED, cause: Nav2 navigation failure (check exact cause string) | Task never reaches VERIFY; failure is logged with a navigation-related cause |
| TC11 | Obstacle blocking the corridor to storage | (check) Same mechanism as TC10, but the obstacle is placed between the collection point and storage, after a successful pickup | IDLE → NAVIGATE_TO_POINT → VERIFY → ATTACH → NAVIGATE_TO_STORAGE (Nav2 fails) → FAILED (magnet released per the FAILED-state rule) → RETURN_HOME → IDLE | FAILED, cause: Nav2 navigation failure to storage (check exact cause string) | Task reaches ATTACH but not RELEASE; magnet is released as part of the FAILED-state handling rather than left attached |
| TC12 | Task request while busy | (check) Send a second `request` while a task is already in a non-IDLE state; exact handling (ignored, queued, or rejected) is not specified in doc 07 and needs confirming on the reference machine | Whatever the implementation defines; not specified in doc 07 | To be confirmed against the implementation (check) | The first task's run is not corrupted or interrupted by the second request; the behaviour matches whatever the reference machine confirms is intended |
| TC13 | Invalid task request | `ros2 topic pub --once /hcw/task_request std_msgs/msg/String "data: 'D'"` (an unknown point, not A/B/C) while the system is IDLE | Stays in IDLE, or reports FAILED immediately depending on implementation (check) | No unsafe motion, no attempt to navigate to an undefined point | Robot does not move; the invalid request does not crash the task manager |

## Run count

13 test cases above. To reach the 20 to 30 total repeated runs required for Week 4, repeat the
three normal cases (TC01 to TC03) two to three times each, and run every other case at least
once:

- TC01, TC02, TC03: 3 runs each (9 runs) — repetition checks reliability of the normal path
- TC04 to TC13: 1 to 2 runs each (10 to 20 runs) — at least one run per case, with the most
  safety-relevant cases (TC09, TC10, TC11) run twice if time allows

This gives a total in the 19 to 29 range, inside the 20 to 30 target once the higher end of the
repeat counts is used.

## Notes

- No results are recorded in this document. Actual outcomes are logged per run in
  `docs/results/run_log_template.csv` (Beni's Task 2) and summarised afterward.
- Several "Set up" and "cause" entries are marked (check) because the exact mechanism or exact
  status string is not fully specified in the docs available at the time this plan was written.
  These should be confirmed and, if needed, corrected by whoever runs the tests on the reference
  machine before relying on this plan during the actual test sessions.
