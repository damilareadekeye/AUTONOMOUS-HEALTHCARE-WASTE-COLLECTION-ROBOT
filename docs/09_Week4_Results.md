# 09 — Repeated Simulation Runs: Results (Week 4)

Last updated: 2026-10-25. All runs on the reference machine (Dami's laptop: WSL2 Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic,
Nav2 1.3.13), Gazebo window closed, real-time factor 1.0. Everything here is simulation only.
Raw data: `docs/results/runs_all_sessions.csv` (every logged run) and `docs/results/runs_final_settings.csv` (runs 56 to 91).

## 1. Headline (final settings, runs 56 to 91)

| Measure | Result |
|---|---|
| **Normal tasks completed** (home, collection point A, B or C, verify, attach, storage, release, report) | **55 of 55 logged tasks (100 %)** under the final settings: A 29, B 13, C 13. 30 of them are the Oct 25 batch (A 18, B 6, C 6); 25 were run on Nov 7 and 8 (sections 6 and 7) |
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
- **Sample size.** 30 normal tasks, 6 fault cases. 55 successes in 55 logged runs supports a true success rate of about 95 % or higher
  (95 % confidence, exact binomial lower bound), not "never fails". Only tasks that finished are logged: tasks that were interrupted
  because the stack was stopped for another reason are not in the log.
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

## 6. Re-check on 2026-11-07, after the code changes of that day

On Nov 7 the code and scripts changed (optional props, demo helpers, stricter cleanup). Navigation settings did not change. Re-checks:

| What | Result |
|---|---|
| Default setup, window closed, 6 tasks (A, B, C twice each), runs 97 to 102 | **6 of 6 completed**; simulation speed 100 %; navigate 13.8 to 40.2 s (mean 25.9), transport 46 to 76 s |
| With the optional hospital-room props, window closed, 3 tasks (A, B, C), runs 103 to 105 | **3 of 3 completed**; idle speed 105 % |
| Other completed tasks that day (runs 92 to 96, window open, with and without props, laptop busy) | 5 of 5 completed |
| Staged faults | not repeated on Nov 7 (6 of 6 on Oct 25) |

**Speed and the laptop.** The same stack that ran at about 100 % of real time on Oct 25 ran at only about 45 to 58 % on Nov 7, until CapCut
(a video editor), Chrome tabs and Task Manager were closed: then it was back at 100 % (Windows CPU load 41 % before, 5 % after). With the Gazebo
window open and nothing else running it ran at 73 to 76 %. For a demo: close other programs, plug in, run `bash scripts/check_speed.sh`.

**Props.** With a loaded laptop, headless idle speed was 58 % without props and 51 % with (about 10 % cost); with the laptop free it was 100 to 105 % either way.
They stay an optional demo mode (`scripts/start_stack.sh gui props`), off by default.

**Slow trips to point A.** In 4 of the 24 completed tasks at A, reaching the collection point took 84 to 98 s instead of the usual 38 to 41 s (runs 74, 93, 96, 103).
B (10 tasks) and C (10 tasks) had none. All 4 still completed. In one case the Nav2 log showed four "failed to make progress" events and one recovery spin while the
machine was loaded (control loop at 10 Hz instead of 20). The cause was not isolated.

**A process bug found and fixed.** A task manager from an earlier run, stuck waiting for Nav2, ignored the normal stop signal and kept running next to the new one, which froze
two batches (one `ros2 param set` command waited forever). `scripts/clean_sims.sh` now force-kills it, `scripts/start_stack.sh` refuses to start if one is still alive,
and the batch scripts put time limits on parameter commands. Those two frozen batches produced no logged runs.

## 7. Re-check on 2026-11-08, after the storage-area change

The magnet's drop point moved from the open floor to the north wall (30.9, -10.95), and the demo mode gained a hazardous-waste storage area (shelves, floor decal,
signs, bins). Navigation settings did not change.

| What | Result |
|---|---|
| Default setup, window closed, 6 tasks (A, B, C twice each), runs 108 to 113 | **6 of 6 completed**; speed 95 %; the first Nav2 start timed out and the start script's retry succeeded |
| With props and the hazard storage area, window closed, 3 tasks (A, B, C), runs 114 to 116 | **3 of 3 completed**; speed 100 % |
| Live demo with the window and props (task 107, A) | completed; the container was set down at (30.9, -10.95), checked in Gazebo |

**Slow trips to point A, updated.** Of 29 completed tasks at A under the final settings, 7 took 84 to 98 s to reach the collection point instead of 38 to 41 s. On Oct 25 it was 1 of 18
(run 74); on Nov 7 and 8 it was 6 of 11 (runs 93, 96, 103, 107, 108, 111), with and without props, at 95 to 100 % speed. B (13 tasks) and C (13 tasks): none. All of them completed.
The extra time (about 45 s) matches Nav2's progress-checker recovery ("failed to make progress", about 10 s each). The cause is not yet identified. For a demo or video,
use B or C for the live task: they have never been slow.

**Nav2 start-up.** On this laptop Nav2's navigation servers sometimes fail to activate within the first 90 s (seen several times on Nov 7 and 8). `scripts/start_stack.sh` waits for
`bt_navigator` to be active and restarts Nav2 up to three times; each retry adds about 3 minutes.
