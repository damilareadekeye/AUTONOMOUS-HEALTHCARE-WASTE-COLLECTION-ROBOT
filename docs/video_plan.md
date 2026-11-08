# 3-Minute Demo Video: Plan, Shot List and Narration

Written for: the team (Dami, David, Beni), to record and edit the demo video for the presentation (maximum 3 minutes).
Facts and numbers are from `docs/09_Week4_Results.md` and `docs/demo_script.md`. Do not add claims that are not in those documents.

## 1. The problem to solve

A full task takes about 4 to 5 minutes of real time with the Gazebo window open, and a failure demo takes about 2 to 3 minutes. The video is 3 minutes.
So: **record the real runs once, then cut and speed them up in CapCut** (the robot's real speed is not the point; the story is). Show the speed-up honestly
with a small "4x" caption.

## 2. Before recording (30 minutes)

| Do | Why |
|---|---|
| Close every other program (browser, chat, Task Manager). Keep only the Ubuntu terminal, the screen recorder and, when needed, VS Code | The simulation slows to half speed when other programs run |
| Plug the laptop in. Windows power mode: Best performance | Same |
| `cd ~/hcw_ws && git pull` | Latest files |
| `bash scripts/start_stack.sh gui props`, wait for `STACK READY` | The demo setup: window, hospital props, hazardous-waste storage area |
| `bash scripts/check_speed.sh` | 70% or more is good; below 40%, restart and close programs |
| Window layout: Gazebo on the left (about two thirds of the screen), the Ubuntu terminal on the right (a third), large font | The viewer sees both the robot and the state names |
| Recorder: OBS Studio with "Display Capture" (records the whole screen, so it also captures the Linux windows), 1080p, 30 fps, microphone off (you add the voice-over later). Windows Game Bar records one app window and may not capture the Gazebo window: test either choice with a 10-second recording first | Cleaner editing |
| Do one full practice task first, then record | The first task after a start sometimes takes longer |

## 3. Recording takes (record each separately, 10 seconds of lead-in and tail)

| Take | What to do | Length to record |
|---|---|---|
| T1 Overview | `bash scripts/demo_camera.sh top 30 -25 38`; hold the view for 15 seconds; then `bash scripts/demo_camera.sh west` for 10 seconds | 30 s |
| T2 Normal task | `bash scripts/demo_camera.sh top 30 -25 38`; run `ros2 run hcw_task request A`; let it finish (RETURN_HOME, IDLE). Switch to `bash scripts/demo_camera.sh follow` for the first 40 seconds, then back to the top view | 4 to 5 min |
| T3 Storage close-up | During the transport to storage, run `bash scripts/demo_camera.sh storage` and keep it until the container is set down | 40 s |
| T4 Failure | `bash scripts/demo_fault.sh wrong B`, then `ros2 run hcw_task request B`, top view; afterwards `bash scripts/demo_fault.sh reset` | 2 to 3 min |
| T5 Results | A still image: open `docs/09_Week4_Results.md` or make one slide with the numbers in section 5 below | 10 s |

## 4. The cut (target 2:55)

| Time | Picture | Speed | Voice-over (read at a calm pace) |
|---|---|---|---|
| 0:00 to 0:15 | Title card, then T1 top view | normal | "Hospitals move sealed waste containers by hand, through busy corridors. Our team built a robot that does this transport, in simulation." |
| 0:15 to 0:35 | T1: overview, then the west corridor with the blue, green and orange containers | normal | "This is a hospital floor in Gazebo. The robot is a TurtleBot 4 with a laser scanner and a camera. Three consulting rooms have containers: blue is A, green is B, orange is C. At the top is the hazardous-waste storage bay." |
| 0:35 to 1:35 | T2: the robot drives to room A, verifies, carries, drops at storage, returns home; terminal visible | 4x, with a "4x" caption | "We ask for a collection from room A. Nav2 drives the robot there. The camera must see the right AprilTag, and only that tag, in five frames in a row. Then a magnet latch picks the container up; here it is simulated. The robot carries it to storage, releases it, reports the task completed and returns home." |
| 1:35 to 1:50 | T3: storage close-up, container set against the wall between the shelves | normal | "The container is set down in the hazardous-waste bay, away from the walkway." |
| 1:50 to 2:30 | T4: wrong container at B; the robot arrives, tries three times, realigns, refuses; terminal shows FAILED with the cause | 4x | "Safety matters more than success. Here we put the wrong container at room B. The robot sees a different tag, tries three times, and refuses. It never picks up the wrong container, and it goes home." |
| 2:30 to 2:50 | T5: results card | still | "In simulation, 67 of 67 normal tasks completed, and all 6 staged faults, a missing or wrong container at each room, were refused for the right reason." |
| 2:50 to 2:58 | Closing card | still | "This is a simulation baseline. Next steps: a dedicated storage room away from people, and testing on real hardware." |

Word count of the voice-over is about 270 words, which fits the time at a calm pace (about 130 words per minute with pauses).

## 5. The results card (one slide)

Title: "Results in simulation".
- 67 of 67 normal tasks completed (collection points A, B, C).
- 6 of 6 faults refused with the right cause (missing or wrong container, at A, B and C).
- Found and fixed two real problems: tasks at room A failed when the tag was at the edge of the camera image, and later stalled 45 s on a one-degree heading dead zone.
- Small print: "Simulation only. One map. Magnet simulated."

## 6. Editing in CapCut (steps)

1. Import T1 to T5. Put them on the timeline in the order of section 4.
2. For T2 and T4: select the clip, Speed, set 4x (or use "Curve" to speed up the long driving parts more, and slow down the verify and release moments).
3. Cut the waiting parts (a robot standing still for more than 3 seconds, the lead-in and tail).
4. Add text captions at the top of the picture with the state names (NAVIGATE_TO_POINT, VERIFY, ATTACH, NAVIGATE_TO_STORAGE, RELEASE, REPORT) as the terminal shows them.
5. Record the voice-over last, in a quiet room, with the finished picture playing. Add the "4x" caption on sped-up parts.
6. Export 1080p, 30 fps. Check the total length: 3:00 or less. Watch it once with sound off: the captions alone must tell the story.

## 7. What not to say or show

- Do not say "real robot", "tested in a hospital" or "100% reliable". Say "in simulation".
- Do not hide the speed-up: caption it.
- Do not show the terminal's error messages from a failed start; restart and retake instead.
- Do not claim the storage bay is a separate safe room; it is a marked hazardous-waste area inside the corridor, and a dedicated room is the next step.
