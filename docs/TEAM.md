# Team

Autonomous Healthcare-Waste Collection Robot — IEEE Rwanda Mentorship Program.
Each person edits only their own section. Facts below come from the Git history of this repository (checked 2026-11-07).

## How the work was done

- The simulation, navigation, perception and task-manager code was built and tested on **Dami's laptop** (the only machine strong
  enough to run the simulation) with **an AI coding assistant (Claude Code)** doing most of the typing, running and measuring,
  under the team's direction: the team made the decisions (world, magnet, what to postpone) recorded in `DECISIONS.md`.
- David and Beni could not run the simulation on their own laptops, so their contributions are documents, small scripts and
  review work, each on its own branch and pull request (see `CONTRIBUTING.md`).

## Dami

- Owns the repository and the reference machine (WSL2 Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic, Nav2) and made the project decisions.
- Most of the commits (27 of 41 at the time of writing, counting merge commits) were made from this machine together with the AI assistant.
- _Add: what you personally decided, tested or learned._

## Beni

- No commits or pull requests in the repository so far (checked 2026-11-07).
- _Beni: add what you worked on, learned or contributed (planning, research, discussions, anything real), and your own pull request
  with it. The unclaimed task `tools/check_repo.py` (a repository check script, Task 4 in `CONTRIBUTING.md`) is open for you._

## David

Seven pull requests merged (#1 to #7):

| Pull request / task | What |
|---|---|
| Task 1 | `README.md` for each package (`hcw_bringup`, `hcw_world`, `hcw_navigation`, `hcw_perception`), plus a follow-up fixing review comments (doors removed, drop points) |
| Task 2 (taken over from Beni) | `docs/results/README.md` and `run_log_template.csv` |
| Task 5 | A distinct colour per container (blue, green, orange, red for the wrong container), models regenerated |
| Task 7 | `docs/results/test_plan.md` (13 test cases), then a follow-up with the real results and confirmed failure causes |
| Task 9 | `docs/GLOSSARY.md`, a plain-language explanation of every term in the project |

He also helped run and observe the simulation on Dami's machine, answered design questions, and checked the demo view.
_David: add what you learned._
