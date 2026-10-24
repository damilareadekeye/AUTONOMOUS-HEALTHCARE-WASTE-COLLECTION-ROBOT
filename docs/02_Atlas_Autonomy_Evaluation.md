# 02 — Atlas-Autonomy Evaluation

Autonomous Healthcare-Waste Collection Robot — IEEE Rwanda Mentorship Program
Last updated: 2026-10-19

Mentor's instruction: start with the official Nav2 simulation as the trusted baseline, then verify
whether Atlas-Autonomy runs successfully.

- Repository: https://github.com/david-eze/Atlas-Autonomy (MIT licence; single author, no outside adoption at time of review)
- Environment: see `01_Environment_Setup.md` (Ubuntu 24.04 WSL2, ROS 2 Jazzy, Gazebo Harmonic 8.15.0, Nav2 1.3.13)
- Atlas is evaluated in a separate workspace (`~/eval/atlas_ws`) so it cannot affect the project workspace (`~/hcw_ws`).
  Do **not** add `~/eval/atlas_ws/install/setup.bash` to `~/.bashrc`.

## Attempt 1 — build exactly as documented (2026-10-19)

```bash
mkdir -p ~/eval/atlas_ws/src && cd ~/eval/atlas_ws/src
git clone https://github.com/david-eze/Atlas-Autonomy.git
cd ~/eval/atlas_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install 2>&1 | tee build.log
source install/setup.bash
ros2 launch robot_bringup mission.launch.py world:=office.world
```

**Result: FAILED — does not build out of the box.**

| Package | Result |
|---|---|
| robot_localization, robot_navigation, robot_mapping, robot_benchmarking, robot_sensors, robot_perception, robot_tf2_diagnostics, robot_safety, robot_mission | Built |
| robot_exploration | **Failed**: `can't copy '.../resource/robot_exploration': doesn't exist or not a regular file` |
| robot_description, robot_planners | Aborted (stopped because another package failed) |
| robot_bringup | Not processed; launch fails with `Package 'robot_bringup' not found` |

### Defects found in the repository

1. **Package name clash with an official ROS package.** Atlas ships its own package named
   `robot_localization` (an EKF *configuration* package) — the same name as the official
   `robot_localization` EKF package installed in `/opt/ros/jazzy`. Its `package.xml` also depends on
   itself, which ROS rejects (`must not "build_depend" on a package with the same name as this package`).
   Building it shadows the official package in that workspace.
2. **Broken Python packaging in `robot_exploration`.** The package is missing the ament resource
   marker file (`resource/robot_exploration`) required by `ament_python` packages; its source is
   nested as `robot_exploration/robot_exploration`.
3. Because of (2), the default colcon build aborts the remaining packages, so `robot_bringup`
   (the launch package) is never built.

## Attempt 2 — minimal workaround build (2026-10-19)

Workarounds applied: added the missing resource marker for `robot_exploration`, and skipped Atlas's
clashing `robot_localization` package so the official one from `/opt/ros/jazzy` is used.

```bash
# New terminal (do not reuse a terminal that sourced the failed build)
cd ~/eval/atlas_ws
rm -rf build install log
PKG=$(dirname "$(find src -path "*robot_exploration*" -name package.xml | head -1)"); echo "$PKG"; ls "$PKG"
mkdir -p "$PKG/resource" && touch "$PKG/resource/robot_exploration"
colcon build --symlink-install --continue-on-error --packages-skip robot_localization 2>&1 | tee build2.log
grep -E "Finished|Failed|Aborted|Summary|rror" build2.log | tail -30
source install/setup.bash
ros2 launch robot_bringup mission.launch.py world:=office.world
```

**Result: FAILED.**

| Package | Result |
|---|---|
| robot_description, robot_mapping, robot_mission, robot_navigation, robot_perception, robot_safety, robot_sensors, robot_tf2_diagnostics, robot_benchmarking | Built |
| robot_exploration | **Failed**: `can't copy '.../config/exploration.yaml': doesn't exist` — the configuration file referenced by `setup.py` is not in the repository |
| robot_planners | **Failed**: `fatal error: robot_planners/astar_planner.hpp: No such file or directory` (same for `dijkstra_planner.hpp`) — the C++ header files for the custom A* and Dijkstra planners are not in the repository |
| robot_bringup | Not processed; `ros2 launch` fails with `Package 'robot_bringup' not found` |

Further defects found:

4. `robot_exploration/setup.py` installs `config/exploration.yaml`, which does not exist in the repository.
5. The `robot_planners` C++ headers (`include/robot_planners/astar_planner.hpp`, `dijkstra_planner.hpp`)
   are missing from the repository. These are the custom planners behind the README's reported
   "70% fewer node expansions" result, so that result cannot be reproduced from the published code.

## Conclusion

**Atlas-Autonomy cannot be built or run from its published repository on ROS 2 Jazzy.** The failures
are caused by missing files (configuration and C++ headers) and packaging errors in the repository
itself, not by our environment: the official Nav2 simulation and Gazebo camera tests pass on the same
machine (see `01_Environment_Setup.md`).

Making it run would require writing the missing planner headers and configuration ourselves and
renaming the clashing package — effectively re-implementing parts of the project, with no way to
check the result against the author's original. Evaluation was therefore stopped after two
time-boxed attempts (about 1 hour in total).

Decision: the project continues on the **official Nav2 simulation** as the navigation baseline, as
the mentor specified. Atlas-Autonomy is not used. The README's self-reported benchmark figures
should not be cited as verified.

Cleanup (optional): `rm -rf ~/eval/atlas_ws`
