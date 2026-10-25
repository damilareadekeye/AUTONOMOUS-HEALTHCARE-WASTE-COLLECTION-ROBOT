# Progress Update — Weeks 3 and 4 (draft for the mentor)

Autonomous Healthcare-Waste Collection Robot — IEEE Rwanda Mentorship Program
Date: 2026-10-25. Written for: the mentor. Edit before sending. Numbers are from `docs/09_Week4_Results.md`.

Subject: Progress update — end-to-end baseline working in simulation, repeated-run results

Dear Sir/Madam,

The baseline you asked for now runs end to end in simulation, and we have repeated-run results. Summary:

**What the system does.** On a request ("collect from point A, B or C") the robot drives to the collection point with Nav2,
verifies the container by its AprilTag (the expected tag must be seen alone in 5 consecutive camera frames), simulates attaching it
(a magnetic latch, modelled by moving the container with the robot), drives to the storage bay, releases it, reports completion and
returns home. A wrong or missing container, or a blocked path, ends in a reported failure and a safe return home; the
task manager never sends velocity commands itself, and perception only publishes observations.

**Results (simulation, 2026-10-25, final settings).**
- Normal tasks: 30 of 30 completed (A 18, B 6, C 6). Mean time from request to report 89 s (median 87 s, max 146 s).
- Fault cases: 6 of 6 correctly rejected (missing or wrong container at A, B and C), each with the right reported cause.
- Earlier today, before one fix: 17 of 18 normal tasks, then 10 of 12 at point A. The failures were traced from saved camera frames
  to the robot stopping 18 degrees off its heading so the tag sat at the edge of the image. A tighter Nav2 goal tolerance and a realign
  step on retry fixed it (30 of 30 afterwards). We report both so the numbers are not flattering.
- Also checked: a box in the corridor (driven around), a fully blocked corridor (clean failure), a request while busy (rejected), an invalid request
  (rejected), and unit tests of the verification rule (8, passing).

**Limits you should know.** Simulation only, one machine, one world (clinic ground floor, shell only: furniture and people were removed
because they slowed the simulation to about 1 to 3 percent of real time). The storage point is a bay in the north corridor, not the real
store room (that area mapped poorly). The robot stops 1.8 m in front of each container and does not enter the rooms.
30 runs support a true success rate of about 88 percent or higher, not "never fails". Not tested: Nav2 failing while carrying the container.

**Schedule.** We are ahead of the timeline (the baseline target date is November 8). Remaining: documentation polish, a reproducibility check
by a second team member following `docs/COMMANDS.md`, a demo script, and optional extras (more hospital detail, a different robot look) which
we have postponed because they would slow the simulation and require re-mapping.

Code, results and the raw run log are in the repository:
https://github.com/damilareadekeye/AUTONOMOUS-HEALTHCARE-WASTE-COLLECTION-ROBOT
(start with `README.md`, then `docs/09_Week4_Results.md`).

We would like to meet when convenient; we can show the system live in about five minutes.

Kind regards,
The project team (Dami, Beni, David)
