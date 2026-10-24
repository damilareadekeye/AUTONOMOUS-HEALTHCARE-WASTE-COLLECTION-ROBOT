# Instructions for AI coding agents working in this repository

You are helping a three-person student team (Dami, Beni, David) build a simulated autonomous
healthcare-waste collection robot (ROS 2 Jazzy, Gazebo Harmonic, Nav2, AprilTag). Read this file first,
then `docs/CONTRIBUTING.md` and `docs/PROJECT_STRUCTURE.md`.

## Where things run (important)

- **Only Dami's machine runs the simulation.** It is the reference machine (WSL2 Ubuntu 24.04, RTX 3070).
  The agent on that machine builds, runs and tests the robot.
- On **any other machine** (Beni's, David's) you work on files only: documents, YAML, small Python
  scripts, model files. **Do not install ROS, Gazebo or NVIDIA drivers, do not try to run the simulation,
  do not change the environment** (no `apt`, no `pip install` over system packages, no conda).
  If a task seems to need the simulation, stop and tell the human to bring it to the reference machine.
- The team sits in the same room. When something needs the simulation or a decision, say so; the human will
  ask the agent on the reference machine.

## Rules

1. **Do only the task you were given** (`docs/CONTRIBUTING.md`, "Tasks"). Do not refactor, rename, reformat or
   "improve" other files. Do not touch the protected files below.
2. **Work on a branch**, never on `main`: `git switch -c <name>/<short-task>` (for example `beni/results-template`).
   Commit small with a clear message, push the branch, and tell the human to open a pull request.
   The reference-machine agent reviews and merges; it checks that the simulation still runs.
3. **Pull before you start** (`git pull`) and do not leave work unpushed at the end of the session.
4. Do not invent results. Numbers in docs must come from a run that the team actually did
   (see `docs/05_Mapping_Navigation_Perception.md`). If you do not know, write "not tested".
5. Keep the style of the surrounding files: short sentences, tables for facts, no marketing language.
6. Never commit `build/`, `install/`, `log/`, large downloads, passwords or tokens.
7. If instructions here conflict with what the human asks, tell the human and ask; do not guess.

## Protected files (change only on the reference machine, after the team agrees)

- `src/**/launch/*.py`, `src/hcw_navigation/config/*.yaml`, `src/hcw_navigation/maps/*`
- `src/hcw_world/config/locations.yaml`, `src/hcw_world/hcw_world/world_builder.py`
- `scripts/*.sh`, `CLAUDE.md`, `.gitignore`
- Anything under `build/`, `install/`, `log/`

## Facts you should not get wrong

- Stack (frozen): Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic 8.15, Nav2 1.3.13, TurtleBot 4 model. No Gazebo Classic.
- World: Open-RMF clinic, ground floor shell only. Named places are in `src/hcw_world/config/locations.yaml`
  (home, collection_A, collection_B, collection_C, storage). Tags: 11 = A, 12 = B, 13 = C, 14 = wrong container.
- Design rule: perception only publishes observations; Nav2 alone moves the robot; a wrong or unstable
  detection leads to wait, retry or failure, never to unsafe motion.
- Goal: end-to-end task success rate over 20 to 30 simulated runs; baseline due 2026-11-08.
- Status and results live in `docs/`; the schedule is in `docs/PROJECT_STRUCTURE.md`.

## When you finish a task

Tell the human: what files you changed, what you checked (and how), and anything you were unsure about.
