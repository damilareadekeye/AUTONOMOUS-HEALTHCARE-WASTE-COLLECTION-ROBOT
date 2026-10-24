# Progress Update — Week 2 (draft for the mentor)

Autonomous Healthcare-Waste Collection Robot — IEEE Rwanda Mentorship Program
Date: 2026-10-24 (due 2026-10-25). Written for: the mentor. Edit before sending.

Subject: Progress update, week 2 — simulation, map, navigation and AprilTag detection working

Dear Sir/Madam,

Here is our week 2 update. The main week 2 items (world, map, named locations, AprilTag detection) are
working in simulation; the exceptions are listed below.

**Done**
- Environment: Ubuntu 24.04 (WSL2), ROS 2 Jazzy, Gazebo Harmonic, Nav2 1.3.13, GPU rendering verified.
  Versions are recorded in the repository.
- Navigation baseline: the official Nav2 TurtleBot 4 simulation passes. Atlas-Autonomy was evaluated twice
  and does not build from its published repository (missing files); we dropped it, as planned.
- World: the Open-RMF Clinic World (ground floor) is our final world. We removed the furniture and the Open-RMF
  door models, because with them the simulation ran at 1 to 3 percent of real time and the doorways were closed.
- Map: built with SLAM Toolbox by driving the clinic's corridors automatically, saved in world coordinates.
- Named locations: Home, three collection points (consulting rooms A, B, C) and a Storage point.
- Containers: yellow containers with AprilTags (tag36h11, ids 11, 12, 13; id 14 reserved as a wrong container).
- Detection: `apriltag_ros` on the robot's camera detected the correct tag at each collection point in 9 of 9 checks.
- Navigation to the named places: 15 of 15 legs completed over three loops (home, A, B, C, storage, home),
  about 6 minutes per loop at real-time speed.

**Not yet done / differences from the plan**
- The storage point is a bay in the north corridor, not the real STORE room: the large north-east hall was
  mapped poorly and the robot could not plan reliably back from it.
- Furniture, people and beds are left out for simulation speed; we will add a few light models.
- The east wing of the clinic and the second floor are not used.
- The task manager (Nav2 Simple Commander state machine), the verification rule, simulated attach and release,
  wrong-container handling and the 20 to 30 repeated runs are next (weeks 3 and 4).

**Schedule**: we are about two to three days behind the original week 2 plan (the map and tags were due
Oct 25 and are done a day later; the timeline allowed 3 to 5 weeks overall). We still aim for the baseline
by Nov 8 and the review meeting in the week of Nov 9.

**Next week (Oct 26 to Nov 1)**: task manager and state machine, verification rule (expected tag seen
consistently before pickup), simulated attach and release, wrong or missing container handling,
first end-to-end run.

Code, documents and results are in the shared repository:
https://github.com/damilareadekeye/AUTONOMOUS-HEALTHCARE-WASTE-COLLECTION-ROBOT
(start with `README.md` and `docs/05_Mapping_Navigation_Perception.md`).

Kind regards,
The project team (Dami, Beni, David)
