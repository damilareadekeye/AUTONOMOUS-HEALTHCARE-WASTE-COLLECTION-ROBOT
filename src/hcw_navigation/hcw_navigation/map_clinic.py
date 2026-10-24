"""Map the clinic ground floor automatically.

Drives the robot along the clinic's own walkable corridors (the Open-RMF navigation graph, level L1)
with Nav2 while SLAM Toolbox builds the map, then saves the map to hcw_navigation/maps/.

    ros2 run hcw_navigation map_clinic [--start-x 8.0 --start-y -31.7] [--out clinic]

Needs: the simulation and `ros2 launch hcw_navigation mapping.launch.py` already running.
The map frame starts where the robot started, so graph (world) coordinates are shifted by the
start pose (the robot must start with yaw 0, which is the launch default).
"""
import argparse
import heapq
import math
import os
import subprocess

import rclpy
import tf2_ros
import yaml
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

LEVEL = 'L1'
# Goals must lie inside the part of the map built so far, so long lanes are driven in short steps.
STEP = 3.0


def load_graph():
    """Return (positions, adjacency) of the L1 navigation graph in world coordinates."""
    maps = get_package_share_directory('rmf_demos_maps')
    with open(os.path.join(maps, 'maps', 'clinic', 'nav_graphs', '0.yaml')) as f:
        level = yaml.safe_load(f)['levels'][LEVEL]
    pos = [(v[0], v[1]) for v in level['vertices']]
    adj = {i: {} for i in range(len(pos))}
    for lane in level['lanes']:
        a, b = lane[0], lane[1]
        d = math.dist(pos[a], pos[b])
        adj[a][b] = d
        adj[b][a] = d
    return pos, adj


def shortest_path(adj, src, dst):
    dist, prev, heap = {src: 0.0}, {}, [(0.0, src)]
    while heap:
        d, u = heapq.heappop(heap)
        if u == dst:
            break
        if d > dist.get(u, math.inf):
            continue
        for v, w in adj[u].items():
            if d + w < dist.get(v, math.inf):
                dist[v], prev[v] = d + w, u
                heapq.heappush(heap, (d + w, v))
    if dst not in dist:
        return None, math.inf
    path = [dst]
    while path[-1] != src:
        path.append(prev[path[-1]])
    return path[::-1], dist[dst]


def make_pose(navigator, x, y, yaw=0.0):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x, pose.pose.position.y = x, y
    pose.pose.orientation.z = math.sin(yaw / 2)
    pose.pose.orientation.w = math.cos(yaw / 2)
    return pose


def robot_xy(navigator, tf_buffer):
    """Robot position in the map frame, or None if the transform is not available yet."""
    try:
        t = tf_buffer.lookup_transform('map', 'base_link', rclpy.time.Time())
        return t.transform.translation.x, t.transform.translation.y
    except Exception:
        return None


def steps(a, b, step=STEP):
    """Points from a (excluded) to b (included), at most `step` metres apart."""
    n = max(1, math.ceil(math.dist(a, b) / step))
    return [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(1, n + 1)]


def go(navigator, x, y, timeout_s=120.0):
    navigator.goToPose(make_pose(navigator, x, y))
    start = navigator.get_clock().now()
    while not navigator.isTaskComplete():
        if (navigator.get_clock().now() - start).nanoseconds / 1e9 > timeout_s:
            navigator.cancelTask()
            break
    return navigator.getResult() == TaskResult.SUCCEEDED


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--start-x', type=float, default=8.0)
    ap.add_argument('--start-y', type=float, default=-31.7)
    ap.add_argument('--out', default='clinic', help='map name (saved in ~/hcw_ws/src/hcw_navigation/maps)')
    args = ap.parse_args()

    pos, adj = load_graph()
    sx, sy = args.start_x, args.start_y

    rclpy.init()
    navigator = BasicNavigator()
    navigator.waitUntilNav2Active(localizer='bt_navigator')
    tf_buffer = tf2_ros.Buffer()
    tf2_ros.TransformListener(tf_buffer, navigator)
    for _ in range(50):                      # let the transform listener fill up
        rclpy.spin_once(navigator, timeout_sec=0.1)
    # Resume from where the robot is now (it may already have driven part of the route).
    now = robot_xy(navigator, tf_buffer) or (0.0, 0.0)
    cur = (now[0] + sx, now[1] + sy)
    here = min(adj, key=lambda i: math.dist(pos[i], cur))
    todo = set(adj) - {here}
    print('Nav2 active. Robot near vertex %d. Mapping %d graph points...' % (here, len(adj)))

    done, failed = 0, 0
    while todo:
        # nearest unvisited vertex by walking distance along the corridors
        best, best_path, best_d = None, None, math.inf
        for v in todo:
            path, d = shortest_path(adj, here, v)
            if path and d < best_d:
                best, best_path, best_d = v, path, d
        if best is None:
            break
        ok = True
        for vid in best_path[1:]:
            prev = (pos[here][0] - sx, pos[here][1] - sy)
            target = (pos[vid][0] - sx, pos[vid][1] - sy)
            ok = True
            for px, py in steps(prev, target):
                ok = go(navigator, px, py)
                if not ok:
                    break
            if not ok:
                break
            todo.discard(vid)
            here = vid
        if ok:
            done += 1
        else:
            failed += 1
            todo.discard(best)
            print('could not reach vertex %d, skipping' % best)
        print('visited %d, failed %d, left %d' % (done, failed, len(todo)))

    maps_dir = os.path.expanduser('~/hcw_ws/src/hcw_navigation/maps')
    os.makedirs(maps_dir, exist_ok=True)
    out = os.path.join(maps_dir, args.out)
    subprocess.run(['ros2', 'run', 'nav2_map_server', 'map_saver_cli', '-f', out,
                    '--ros-args', '-p', 'save_map_timeout:=10.0', '-p', 'use_sim_time:=true'], check=False)
    print('map saved to %s.yaml / .pgm' % out)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
