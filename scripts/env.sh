#!/usr/bin/env bash
# Source this in every terminal:  source ~/hcw_ws/scripts/env.sh
# Loads ROS 2 Jazzy, the Open-RMF clinic assets (~/eval/rmf_ws) and our workspace.
source /opt/ros/jazzy/setup.bash
[ -f "$HOME/eval/rmf_ws/install/setup.bash" ] && source "$HOME/eval/rmf_ws/install/setup.bash"
[ -f "$HOME/hcw_ws/install/setup.bash" ] && source "$HOME/hcw_ws/install/setup.bash"
export ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-11}
