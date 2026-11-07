#!/usr/bin/env bash
# Move the Gazebo window's camera for a demo (the stack must be running with the window: scripts/start_stack.sh gui).
#   scripts/demo_camera.sh top        # whole building from above (default)
#   scripts/demo_camera.sh west       # the west corridor with collection points A, B, C and Home
#   scripts/demo_camera.sh follow     # follow the robot
#   scripts/demo_camera.sh robot      # jump to the robot once (no follow)
#   scripts/demo_camera.sh top 30 -24 55    # custom: x y height of a top-down view
source "$HOME/hcw_ws/scripts/env.sh"
mode=${1:-top}
pose() {   # pose <x> <y> <z>  (looking straight down)
  gz service -s /gui/move_to/pose --reqtype gz.msgs.GUICamera --reptype gz.msgs.Boolean --timeout 3000 \
    --req "pose: {position: {x: $1, y: $2, z: $3}, orientation: {x: 0, y: 0.7071068, z: 0, w: 0.7071068}}"
}
entity() { gz service -s "$1" --reqtype gz.msgs.StringMsg --reptype gz.msgs.Boolean --timeout 3000 --req 'data: "turtlebot4"'; }
case "$mode" in
  top)    pose "${2:-26}" "${3:--24}" "${4:-50}" ;;
  west)   pose 11 -26 22 ;;
  follow) entity /gui/follow ;;
  robot)  entity /gui/move_to ;;
  *)      echo "usage: demo_camera.sh top|west|follow|robot  or  top <x> <y> <height>"; exit 2 ;;
esac
