# 09 — Repeated Simulation Runs: Results (Week 4)

Last updated: 2026-10-25. All runs on the reference machine (Dami's laptop: WSL2 Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic,
Nav2 1.3.13), Gazebo window closed, real-time factor 1.0. Everything here is simulation only.
Raw data: `docs/results/runs_all_sessions.csv` (every logged run) and `docs/results/runs_final_settings.csv` (runs 56 to 91).

## 1. Headline (final settings, runs 56 to 91)

| Measure | Result |
|---|---|
| **Normal tasks completed** (home, collection point A, B or C, verify, attach, storage, release, report) | **30 of 30 (100 %)**: A 18, B 6, C 6 |
| **Fault cases handled correctly** (missing or wrong container: the task must FAIL with the right cause, put the container back, return home) | **6 of 6** |
| Time from request to REPORT (normal tasks) | mean 89 s, median 87 s, min 85 s, max 146 s |
| Time per stage (mean of the 30) | navigate to the collection point 33 s (one run 98 s), verify 0.5 s, transport to storage 56 s |
| A whole task including the drive home | about 3.3 minutes |
| A fault case (3 verification attempts, realign, drive home) | about 1.3 to 3 minutes |

How the 30 normal tasks were run: 12 consecutive tasks at A (runs 56 to 67), then 18 tasks A, B, C round robin (runs 68 to 85), each started by `ros2 run hcw_task request <point>` from `scripts/run_batch.sh`, with no manual step in between.

## 2. History: what the same system did before the last fix

The numbers above are not the whole story. The system went through these batches, and the last change fixed a real fault:

| Runs | Settings | Normal tasks | Fault cases |
|---|---|---|---|
| 20 to 43 | Nav2 goal tolerance 0.25 m / 0.25 rad | 17 of 18 (the one failure was at A: no tag detected) | 6 of 6 failed as designed, but one reported "no tag" instead of "wrong container" because the test setup did not place the container |
| 44 to 55 (point A only) | same | 10 of 12 (two more failures at A) | |
| 56 to 67 (point A only) | **tolerance 0.15 m / 0.10 rad and realign retry** | **12 of 12** | |
| 68 to 91 | same as above (final) | **18 of 18** | **6 of 6, correct cause each time** |

Root cause of the failures at A (found with camera frames saved at the failure, `docs/images/incident_task51_camera.png` and
`incident_task55_camera.png`): the robot stopped about 18 degrees off its heading, so the container's tag sat at the edge of the
camera image and could not be read. Details in `08_Week3_Task_Manager_Results.md`, section 4d. With the final settings no such failure
was seen in 30 normal runs; that is evidence, not proof that it can never happen.

## 3. Fault cases (final batch, runs 86 to 91)

| Run | Case | Result | Cause reported |
|---|---|---|---|
| 86 | Missing container at A | FAILED, as designed | no container tag detected (expected 11) |
| 87 | Wrong container at A (tag 12 in its place) | FAILED, as designed | wrong container (tag(s) [12] seen, expected 11) |
| 88 | Missing container at B | FAILED, as designed | no container tag detected (expected 12) |
| 89 | Wrong container at B (tag 13) | FAILED, as designed | wrong container (tag(s) [13] seen, expected 12) |
| 90 | Missing container at C | FAILED, as designed | no container tag detected (expected 13) |
| 91 | Wrong container at C (tag 11) | FAILED, as designed | wrong container (tag(s) [11] seen, expected 13) |

Earlier separate checks (`08_Week3_Task_Manager_Results.md`, 4b and 4c): a request while busy is rejected, an invalid request is rejected, a
box in the corridor that leaves a gap is driven around (completed), and a corridor blocked completely makes the task fail cleanly
("navigation to the collection point failed" after about 64 s) with recovery on the next task.

## 4. Things you must not read into these numbers

- **Simulation only.** No real robot, no real container, no real hospital. Nothing here supports a claim about real deployment.
- **Narrow conditions.** One world (clinic ground floor, shell only, no furniture or people), one robot start (home), one machine,
  containers always in the same places, fixed lighting.
- **The magnet is simulated.** The container model is moved with the robot (it floats above it while carried). The robot stops 1.8 m
  in front of the container; it never enters a room (the doorways are blocked on the map).
- **Faults were injected by moving container models**, not by real failures of the camera or the robot. The unstable-tag case is
  tested by unit tests of the verification rule, not by a live run.
- **Sample size.** 30 normal tasks, 6 fault cases. 30 successes in 30 runs supports a true success rate of about 88 % or higher
  (95 % confidence, exact binomial lower bound), not "never fails".
- **One slow run:** run 74 (A) needed 98 s to reach the collection point instead of about 39 s, then completed. The cause was not
  investigated (probably a Nav2 recovery manoeuvre).
- **Not tested:** Nav2 failing during the drive to storage with the container attached; more than one task at once (a second request is
  rejected); repeated runs on a different map or after a restart of the machine.
- **The storage point** is a bay in the north corridor, not the real STORE room (see `05_Mapping_Navigation_Perception.md`).

## 5. How to reproduce

```bash
cd ~/hcw_ws && git pull && source scripts/env.sh
scripts/start_stack.sh                          # about 1.5 minutes, prints STACK READY
scripts/run_batch.sh 18 --with-failures         # 18 normal tasks + 6 fault cases, about 1.5 hours, unattended
python3 scripts/summarize_runs.py --from-run <first run id of the batch>
```
Rows are appended to `~/hcw_ws/results/runs.csv`; `docs/COMMANDS.md` has every other command.
