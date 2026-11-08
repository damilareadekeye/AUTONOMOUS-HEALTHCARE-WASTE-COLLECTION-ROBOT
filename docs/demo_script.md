# Demo Script (about 8 minutes)

Written for: the people presenting (Dami, David, Beni), to run the live demo on Dami's laptop in front of judges or the mentor.
Everything runs on **Dami's laptop**. A projector shows the Gazebo window; the presenter points at the screen and talks; a second
person types the commands. Numbers quoted here are from `docs/09_Week4_Results.md`.

## 1. Before the demo (30 minutes ahead)

| Do | Why |
|---|---|
| Plug the laptop in, set Windows power mode to best performance, close every other program (browser, chat, video) | The simulation uses most of the CPU. With other programs open it ran at about 45% of real time instead of 75% |
| Open an Ubuntu terminal and run `cd ~/hcw_ws && git pull` | Latest code |
| `bash scripts/start_stack.sh gui props` and wait for `STACK READY` (about 2 minutes) | Starts the simulation with the Gazebo window, the hospital-room props, Nav2, tag detection and the task manager |
| `bash scripts/demo_camera.sh top 30 -25 38` | Whole building seen from above |
| `bash scripts/check_speed.sh` | 70% or more is good. 40 to 70%: it works, tasks take 5 to 8 minutes. Below 40%: `bash scripts/clean_sims.sh`, close programs, start again |
| Do **one complete practice task**: `ros2 run hcw_task request A`, wait until it prints `IDLE` | Confirms everything works on this day, on this projector |
| Leave the terminal visible next to the window: it prints every step | The audience can read the state names as the robot works |

## 2. The talk (what to say and do)

**Minute 0 to 1: the problem.** "Hospitals move sealed waste containers from rooms to a storage area by hand. Staff walk the corridors repeatedly,
which costs time and exposes them to risk. We built a robot that does this transport. It carries only sealed, empty containers
in this prototype; it never opens or handles the waste itself."

**Minute 1 to 2: the world (point at the projector).** "This is a simulated hospital ground floor in Gazebo, built from the Open-RMF clinic.
The robot is a TurtleBot 4 with a laser scanner and a camera. It starts in the small room at the bottom-left (Home). Along the west corridor there are
three consulting rooms with a container at the door: blue is A, green is B, orange is C. The storage bay is in the north corridor, dressed as a hazardous-waste store: amber hazard-striped floor, shelves, warning signs, yellow bins. It is a marked restricted area, not a separate room; say that a dedicated room away from people is the next step.
Beds, desks and other props in the rooms are decoration for this demo." (Do not claim the props matter for the robot.)

**Minute 2 to 6: one live task.** Say "We ask the robot to collect the container from point A", then type:
```bash
ros2 run hcw_task request A
```
Narrate each line the terminal prints, in plain words:

| Terminal says | You say |
|---|---|
| `NAVIGATE_TO_POINT` | "It plans a route with Nav2 on a map we built with SLAM, and drives to room A" |
| `VERIFY ... attempt 1 of 3` | "Its camera looks for the tag on the container. It must see the right tag, and only that tag, in 5 frames in a row. One noisy frame is not enough" |
| `ATTACH` | "Verified. The magnet latches the container" |
| `NAVIGATE_TO_STORAGE` | "It carries it along the corridor to the hazardous-waste bay. Nav2 avoids obstacles on the way" (use `bash scripts/demo_camera.sh storage` to show the bay) |
| `RELEASE`, `REPORT COMPLETED` | "The magnet lets go, the robot reports the task as completed" |
| `RETURN_HOME`, `IDLE` | "It drives back to Home and waits for the next task" |

Use the mouse to zoom and rotate the view, or `bash scripts/demo_camera.sh follow` to follow the robot, and `bash scripts/demo_camera.sh top 30 -25 38` to go back to the overview.
If the speed is low (check with `check_speed.sh` before), say "the simulation runs slower than real time on this laptop; at full speed a whole task takes about 3.5 simulated minutes". Do not claim anything about how long a real robot would take: we have no measurement for that.

**Explain the magnet (important, be honest).** "The container is attached with a magnetic latch. In the simulation, the magnet is modelled: when the camera
has verified the container, the container model moves with the robot, and it is put down at storage. We chose this because simulating a physical grip is slow
and unreliable. It tests the whole chain (task, navigation, verification, handover), not the mechanical grip."

**Minute 6 to 7: safety (optional if time; takes about 3 minutes live).** "What if it is the wrong container?" Type:
```bash
bash scripts/demo_fault.sh wrong B
ros2 run hcw_task request B
```
Narrate: "We put the wrong container at room B. The robot arrives, the camera sees a different tag, it tries three times, realigns, and then **refuses and reports a failure**.
It never picks up the wrong thing and never moves unsafely." Afterwards: `bash scripts/demo_fault.sh reset`.
(If time is short, skip the live failure and describe it; the log has all six cases.)

**Minute 7 to 8: results.** "In simulation, over several test sessions, 67 normal tasks at all three rooms: all 67 completed. We staged 6 faults, a missing and a wrong container at each room: all 6 were
correctly refused, with the right reason. We also found and fixed two real problems on the way. Early on, 3 of 30 tasks, all at room A, failed because the robot stopped slightly turned and the tag was at the edge of the camera image: we saved camera frames at the failures,
found the cause and tightened the arrival tolerance. Later, trips to room A sometimes stalled for 45 seconds: we logged the robot's position, found a one-degree dead zone in the heading tolerance, and relaxed it. After that, no stalls."

## 3. If something goes wrong

| Problem | What to do |
|---|---|
| Nothing happens after `request` | Check the terminal for `STACK READY`. If missing: `bash scripts/clean_sims.sh`, wait 10 seconds, `bash scripts/start_stack.sh gui props` |
| The robot is very slow | `bash scripts/check_speed.sh`. Close programs. If still slow, say so, and show the results instead (below) |
| The task fails when it should not | Say so honestly: "it is a simulation and this is a failure case; we log it". Show `docs/09_Week4_Results.md`. Run `bash scripts/demo_fault.sh reset` and try again |
| Everything is broken | Show `docs/09_Week4_Results.md`, `docs/images/clinic_map_locations.png` and the run log `docs/results/runs_final_settings.csv` |

## 4. Questions you may get (honest answers)

| Question | Answer |
|---|---|
| Is this a real robot? | No. It is a simulation: ROS 2, Gazebo and Nav2. The design is for a real TurtleBot-class robot, but nothing here proves it works in a real hospital |
| Did you train an AI model? | No. Navigation uses Nav2 and a map; container identification uses AprilTag markers, which need no training data. A learned detector (YOLO) is a possible later experiment |
| Why markers and not recognising the container? | Markers are reliable, give the identity and the position, and need no dataset. Perception only reports what it sees; Nav2 alone moves the robot |
| How reliable is it? | 67 of 67 normal tasks and 6 of 6 fault cases in simulation. 67 runs supports a true success rate of about 96% or higher; it is not a guarantee |
| What did you not test? | Nav2 failing while carrying a container; real hardware; other maps; crowds. The storage point is a bay in the corridor, not the real store room |
| What about the magnet? | Simulated: the container moves with the robot (see above) |
| Who built it? | The three of us, with an AI coding assistant (Claude Code) running on Dami's laptop that wrote most of the code and ran the tests under our direction. Decisions are in `docs/DECISIONS.md`, contributions in `docs/TEAM.md` |
| Why is the hospital empty / why are there only some props? | Detailed furniture made the simulation 30 to 100 times slower, so we kept the building and added a few light props. More detail is a later improvement |
