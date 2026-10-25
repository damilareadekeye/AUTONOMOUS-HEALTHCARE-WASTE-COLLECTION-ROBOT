# Test Plan — Repeated Simulation Runs (Week 4)

Based on `docs/07_Task_Manager_Design.md`, section 4 (state machine) and section 7 (test
scenarios), corrected against the real implementation (`task_manager.py`) and the actual Week 4
results (`docs/09_Week4_Results.md`). This plan does not contain run results; those are logged
per run in `~/hcw_ws/results/runs.csv` and summarised in `docs/results/README.md`,
`docs/results/runs_all_sessions.csv` and `docs/results/runs_final_settings.csv`.

## How to read this table

- **Set up**: how to produce the scenario in simulation, in words.
- **Expected states**: the state-machine path from `IDLE` the task should take, per doc 07
  section 4.
- **Expected result**: the exact state, result and cause the task manager reports.
- **Pass rule**: what must be true for the run to count as a pass.

## Test cases

| ID | Scenario | Set up | Expected states | Expected result | Pass rule |
|---|---|---|---|---|---|
| TC01 | Normal task, point A | `ros2 run hcw_task request A`, correct tag (11) in place at A | IDLE → NAVIGATE_TO_POINT → VERIFY → ATTACH → NAVIGATE_TO_STORAGE → RELEASE → REPORT → RETURN_HOME → IDLE | COMPLETED | Robot reaches A, tag 11 verified, container moves with robot to storage, robot returns home |
| TC02 | Normal task, point B | Same as TC01, `request B`, tag 12 at B | Same full sequence | COMPLETED | Same as TC01, for B / tag 12 |
| TC03 | Normal task, point C | Same as TC01, `request C`, tag 13 at C | Same full sequence | COMPLETED | Same as TC01, for C / tag 13 |
| TC04 | Wrong container at A | `ros2 param set /task_manager reset_container false`, then move tag 12's container into A's place. Confirmed working: run 87, tag 12 at A | IDLE → NAVIGATE_TO_POINT → VERIFY (fails) → wait, retry, up to 3 attempts → FAILED → RETURN_HOME → IDLE | FAILED, cause: `wrong container (tag(s) [12] seen, expected 11)` | Task never reaches ATTACH; robot ends back at home |
| TC05 | Wrong container at B | Same mechanism, tag 13's container into B's place. Confirmed: run 89 | Same as TC04 | FAILED, cause: `wrong container (tag(s) [13] seen, expected 12)` | Same as TC04 |
| TC05b | Wrong container at C | Same mechanism, tag 11's container into C's place. Confirmed: run 91 | Same as TC04 | FAILED, cause: `wrong container (tag(s) [11] seen, expected 13)` | Same as TC04 |
| TC06 | Missing container at A | `ros2 param set /task_manager reset_container false`, container removed/not reset at A. Confirmed: run 86 | IDLE → NAVIGATE_TO_POINT → VERIFY (no tag) → wait, retry, up to 3 attempts → FAILED → RETURN_HOME → IDLE | FAILED, cause: `no container tag detected (expected 11)` | Task never reaches ATTACH; robot ends back at home |
| TC07 | Missing container at B | Same mechanism at B. Confirmed: run 88 | Same as TC06 | FAILED, cause: `no container tag detected (expected 12)` | Same as TC06 |
| TC07b | Missing container at C | Same mechanism at C. Confirmed: run 90 | Same as TC06 | FAILED, cause: `no container tag detected (expected 13)` | Same as TC06 |
| TC10 | Obstacle blocking the corridor to a collection point | Place an obstacle in the corridor between home and a collection point. Tested: fails after about 64 s | IDLE → NAVIGATE_TO_POINT (Nav2 fails) → FAILED → RETURN_HOME → IDLE | FAILED, cause: `navigation to the collection point failed` | Task never reaches VERIFY |
| TC10b | Obstacle that leaves a gap | A box in the corridor that leaves a gap for the robot to drive around. Tested | Normal full sequence, with a detour | COMPLETED | Task completes despite the obstacle |
| TC11 | Obstacle blocking the corridor to storage | Same mechanism as TC10, obstacle placed between the collection point and storage, after a successful pickup. Not yet tested | IDLE → NAVIGATE_TO_POINT → VERIFY → ATTACH → NAVIGATE_TO_STORAGE (Nav2 fails) → FAILED → RETURN_HOME → IDLE | FAILED, cause: `navigation to storage failed`. The container is put back at its original place, not "released" at storage | Task reaches ATTACH but not RELEASE; container ends back at its original collection point |
| TC12 | Task request while busy | Send a second `request` while a task is already running. Tested | N/A — first task's run is undisturbed | State `BUSY`, result `REJECTED`, cause `a task is already running`. Rejected, not queued | The first task's run is not disturbed; the second request is cleanly rejected |
| TC13 | Invalid task request | `ros2 topic pub --once /hcw/task_request std_msgs/msg/String "data: 'Z'"`. Tested | Stays in IDLE | State `IDLE`, result `REJECTED`, cause `invalid request "Z" (use A, B or C)` | Robot does not move |
| TC14 | Magnet failure (attach) | To be defined — covers `magnet failed to attach: <text>` | Reaches VERIFY, fails at ATTACH | FAILED, cause: `magnet failed to attach: <text>` | Task does not proceed to NAVIGATE_TO_STORAGE |
| TC15 | Magnet failure (release) | To be defined — covers `magnet failed to release: <text>` | Reaches NAVIGATE_TO_STORAGE, fails at RELEASE | FAILED, cause: `magnet failed to release: <text>` | Task does not reach REPORT as COMPLETED |

Not included as simulation test cases: an unstable tag that briefly recovers or never stabilises.
This cannot be reliably produced in the simulation and is instead covered by the unit test
`src/hcw_perception/test/test_verifier_rule.py`.

## Run count (actual, final settings)

The real final batch (`docs/09_Week4_Results.md`) covers **30 normal tasks** (A 18, B 6, C 6,
all COMPLETED) plus **6 fault cases** (3 missing-container, 3 wrong-container, one at each of A,
B, C, all FAILED with the correct cause), for **36 runs total**. This exceeds the original 20 to
30 target. Earlier batches under looser Nav2 settings (runs 20-55) showed intermittent failures
at point A that were root-caused and fixed (tighter goal tolerance, realign retry); see
`docs/09_Week4_Results.md` section 2 for that history. TC11, TC14 and TC15 are not yet covered by
a real run and remain open for a future test session.

## Notes

- Results are not recorded in this document. See `docs/results/README.md` for where the real
  data lives and how success rates are computed.
- TC08 and TC09 (unstable tag) were removed from the simulation test cases and are covered by a
  unit test instead.
- A 100% success rate on these runs does not mean the system never fails; see
  `docs/09_Week4_Results.md` section 4 for the statistical caveat.
