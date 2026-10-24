# Contributing: how Beni and David (and Dami) work together

Last updated: 2026-10-24

## How we work

- The team works in the same room. Dami's machine runs the simulation; everyone watches it there.
- Beni and David work on their own laptops on **small, file-only tasks** (below), push their own branches,
  and so appear as contributors on GitHub. Nobody installs the simulation stack on a second machine.
- The agent on Dami's machine knows the whole project. Agents on other machines only see the repository,
  so they follow `CLAUDE.md` (in the repo root) and do just the task they are given.
- Anything that needs the simulation, a map, Nav2 settings or a launch file is done on Dami's machine, together.

## One-time setup on your own laptop (about 10 minutes, no ROS needed)

```bash
git config --global user.name  "Your Name"
git config --global user.email "your-github-email"
git clone https://github.com/damilareadekeye/AUTONOMOUS-HEALTHCARE-WASTE-COLLECTION-ROBOT.git
cd AUTONOMOUS-HEALTHCARE-WASTE-COLLECTION-ROBOT
```
You can do this on Windows with Git and VS Code; WSL is not required for the tasks below.
Dami must first add you as a collaborator (GitHub: Settings, Collaborators). Python 3 with `pyyaml`
and `opencv-python` is only needed for task 4.

If you use an AI agent (for example Claude Code) in the cloned folder, it will read `CLAUDE.md` automatically.
Start it with: "Read CLAUDE.md and docs/CONTRIBUTING.md. My task is Task N. Do only that task."

## Daily routine

```bash
git pull
git switch -c yourname/short-task        # for example: david/package-readmes
# ... do the task, check it, then:
git add <only the files of your task>
git commit -m "Short, clear message"
git push -u origin yourname/short-task
```
Then open a pull request on GitHub (a yellow button appears after the push) and tell Dami's machine's agent
to review it. It will check the files, check that the simulation still runs, and merge.

## Tasks (lightweight, file-only)

Each task lists the files you may change. Do not edit anything else. Mark a task done by telling the team.

### Task 1 (David): README for every package
Write `README.md` for each of `src/hcw_bringup`, `src/hcw_world`, `src/hcw_navigation`, `src/hcw_perception`.
Each README: purpose (2 sentences), the launch or run commands from `docs/04_Clinic_Simulation_Bringup.md` and
`docs/05_Mapping_Navigation_Perception.md`, the important files in the package, and which topics it uses.
Files you may add: those four `README.md` files. Check: every command you write appears in the docs; do not
invent options. Run time: about 1 hour.

### Task 2 (Beni): results template for the repeated runs (Week 4)
Create `docs/results/README.md` and `docs/results/run_log_template.csv`. The CSV has one row per run and these
columns: `run_id, date, collection_point, wrong_container (yes/no), obstacle (yes/no), success (yes/no),
time_navigate_s, time_verify_s, time_transport_s, failure_cause, notes`. The README explains each column in
one line, how to compute the task success rate, and a table to fill in (success rate per collection point).
The numbers stay empty: they come from real runs. Files: those two. Run time: about 45 minutes.

### Task 3 (David or Beni): hospital detail ideas (research only, nothing is installed)
Write `docs/ideas/hospital_models.md`: a table of 8 to 10 simple hospital items we could add to the
clinic later (bed, trolley, waste bin, wheelchair, IV stand, screen, bench, cabinet ...) with where to get a free
Gazebo model (name and link on https://app.gazebosim.org/fuel), its licence, and a note on how detailed it
looks (simple or complex). Prefer simple models: complex ones slow the simulation to a crawl (see
`docs/04_Clinic_Simulation_Bringup.md`, section "Findings"). Files: that one. Run time: about 1 hour.

### Task 4 (Beni): a repository check script that runs without ROS
Write `tools/check_repo.py` (new folder `tools/`). It must run on any laptop with plain Python 3 and
`pyyaml`, and: (a) parse every `*.yaml` under `src/` and `docs/`, (b) check every `model.sdf` under
`src/hcw_world/models/` is well-formed XML, (c) compile every `*.py` under `src/` (`py_compile`), and
(d) check every `docs/*.md` link to another file in the repository points to a file that exists. Print one
line per problem and exit with code 1 if there is any, else print `OK` and exit 0. Do not install anything
for it. Files: `tools/check_repo.py`. Check: run it; it must print `OK` on a fresh clone. Run time: about 1.5 hours.
(The reference-machine agent will review it and add it to the routine.)

### Task 5 (David): container colours
In `src/hcw_world/scripts/make_tag_models.py` the container is yellow (`<ambient>0.95 0.8 0.1 1</ambient>`).
Make the colour a per-tag setting at the top of that file (for example `COLORS = {11: (0.9, 0.3, 0.1), ...}`)
so that A, B, C are visibly different colours and the wrong container (14) is a clearly different colour.
Keep the AprilTag texture exactly as it is. Run the script (needs Python 3, `opencv-python`, `numpy`):
`python3 src/hcw_world/scripts/make_tag_models.py`, and commit the changed script **and** the regenerated
`model.sdf` files. Do not change sizes or tag ids. Dami's machine will check them in Gazebo. Run time: about 1 hour.

### Task 6 (all): the team page
Each person adds one paragraph about their part of the project to `docs/TEAM.md` (name, role, what they
worked on, what they learned). Each person edits only their own section. Run time: 20 minutes.

## What not to do

- Do not run `colcon build`, `ros2 ...` or `gz ...` on your own laptop.
- Do not edit the protected files listed in `CLAUDE.md`.
- Do not merge your own pull requests, and do not push to `main`.
- Do not use two different agents on the same task at the same time.

## When something goes wrong

Stop, do not "fix" it with more commands, and ask in the room. If a command prints an error, copy the full
text to the agent on Dami's machine. The Git history keeps every earlier version, so nothing is lost.
