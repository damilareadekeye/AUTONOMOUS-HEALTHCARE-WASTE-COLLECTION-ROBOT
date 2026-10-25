# hcw_perception

Runs AprilTag detection on the robot's camera and decides whether the expected container tag
is verified. It only observes: it never publishes motor commands.

## Run

```bash
ros2 launch hcw_perception apriltag.launch.py
```

Check what tags are visible:
```bash
ros2 run hcw_perception tag_monitor              # print changes until Ctrl+C
ros2 run hcw_perception tag_monitor --collect 6  # listen 6 s, print the ids seen, then exit
```

## Important files
- `launch/apriltag.launch.py` — starts AprilTag detection and the verifier node
- `config/apriltag.yaml` — AprilTag detector configuration
- `hcw_perception/tag_monitor.py` — quick check of which tag ids the camera sees
- `hcw_perception/verifier.py` — applies the verification rule (expected tag seen in 5
  consecutive messages, no other tag in view)

## Topics
- In: `/rgbd_camera/image` (remapped to `image_rect`), `/rgbd_camera/camera_info` (remapped to
  `camera_info`), `/perception/expected_tag` (Int32, tag id to look for, 0 = not looking)
- Out: `/detections` (apriltag_msgs/AprilTagDetectionArray), a TF frame per tag (`tag_A`,
  `tag_B`, `tag_C`, `tag_wrong`), `/perception/target_status` (String, JSON)
