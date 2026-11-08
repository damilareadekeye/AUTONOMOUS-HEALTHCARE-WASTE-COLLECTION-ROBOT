#!/usr/bin/env bash
# Move the Gazebo window's camera for a demo (the stack must be running with the window: scripts/start_stack.sh gui).
#   scripts/demo_camera.sh top        # whole building from above (default)
#   scripts/demo_camera.sh west       # the west corridor with collection points A, B, C and Home
#   scripts/demo_camera.sh storage    # the storage bay with its shelves
#   scripts/demo_camera.sh follow     # follow the robot
#   scripts/demo_camera.sh robot      # jump to the robot once (no follow)
#   scripts/demo_camera.sh top 30 -24 55    # custom: x y height of a top-down view
source "$HOME/hcw_ws/scripts/env.sh"
mode=${1:-top}
pose() {   # pose <x> <y> <z>  (looking straight down); first stops any "follow" so the view stays where we put it
  gz service -s /gui/follow --reqtype gz.msgs.StringMsg --reptype gz.msgs.Boolean --timeout 2000 --req 'data: ""' >/dev/null 2>&1
  gz service -s /gui/move_to/pose --reqtype gz.msgs.GUICamera --reptype gz.msgs.Boolean --timeout 3000 \
    --req "pose: {position: {x: $1, y: $2, z: $3}, orientation: {x: 0, y: 0.7071068, z: 0, w: 0.7071068}}"
}
entity() { gz service -s "$1" --reqtype gz.msgs.StringMsg --reptype gz.msgs.Boolean --timeout 3000 --req 'data: "turtlebot4"'; }
case "$mode" in
  top)    pose "${2:-26}" "${3:--24}" "${4:-50}" ;;
  west)   pose 11 -26 22 ;;
  storage) pose 31 -12 14 ;;
  follow) entity /gui/follow ;;
  tilt)   # slanted camera angle (about 50 degrees down, looking along +x) at the robot: use before chase
          gz service -s /gui/follow --reqtype gz.msgs.StringMsg --reptype gz.msgs.Boolean --timeout 2000 --req 'data: ""' >/dev/null 2>&1
          gz service -s /gui/move_to/pose --reqtype gz.msgs.GUICamera --reptype gz.msgs.Boolean --timeout 3000 \
            --req "pose: {position: {x: ${2:-4}, y: ${3:--31.7}, z: ${4:-8}}, orientation: {x: 0, y: 0.4349655, z: 0, w: 0.9004471}}" ;;
  chase)  entity /gui/follow    # follow from high above: chase [dx dy dz] (default -1.5 0 9), stays clear of the walls
          gz service -s /gui/follow/offset --reqtype gz.msgs.Vector3d --reptype gz.msgs.Boolean --timeout 3000 \
            --req "x: ${2:--1.5} y: ${3:-0} z: ${4:-9}" ;;
  robot)  entity /gui/move_to ;;
  *)      echo "usage: demo_camera.sh top|west|storage|follow|robot  or  top <x> <y> <height>"; exit 2 ;;
esac
