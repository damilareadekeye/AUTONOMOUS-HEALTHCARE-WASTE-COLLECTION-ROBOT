# Team decisions

Newest first. Add a line when the team decides something.

| Date | Decision | Why |
|---|---|---|
| 2026-10-25 | **No hospital detail and no robot redesign before the baseline is done** (Weeks 1 to 4 complete, 20 to 30 runs finished). Revisit afterwards. | Nothing in our system is trained (Nav2, SLAM and AprilTag need no training data), so neither change needs training. But more furniture slows the simulation (405 models gave about 3 % real time; 700 gave about 1 %) and means making the map again; a new robot shape means re-tuning Nav2 and re-testing everything. The baseline matters first. |
| 2026-10-25 | Keep the TurtleBot 4 as the robot. | It works; a redesign risks the working navigation |
| 2026-10-25 | Attach and release are a **simulated magnet**: the container model follows the robot (described in the demo as a magnetic latch) | A physical grip in Gazebo is slow to build and unreliable on demo day |
| 2026-10-25 | Long runs are automated (`scripts/run_batch.sh`) and need no AI | Saves AI usage; anyone can start them |
| 2026-10-24 | The Open-RMF clinic ground floor (shell only) is the final world. Containers: yellow bins with AprilTags 11, 12, 13 (14 = wrong container) | It runs at real time and works with Nav2 |
| 2026-10-24 | Storage is a bay in the north corridor, not the real STORE room | The north-east hall is poorly mapped and Nav2 could not plan reliably back from it |
| 2026-10-24 | Only Dami's machine runs the simulation; Beni and David work on file-only tasks (`docs/CONTRIBUTING.md`) | Other machines cannot run it |

## When detail can be added later (after the baseline)

A small number (about 10) of simple models, one batch at a time: add them, measure `real_time_factor`
(stay above 0.8), re-make the map (`ros2 launch hcw_navigation mapping.launch.py` and `map_clinic`, about 30 minutes,
then `seal_room_doors.py`), and re-run `scripts/run_batch.sh`. Ideas: `docs/ideas/hospital_models.md` (Task 3).
