# PRD-06: ROS2 Integration

> Module: SLAM-MIPSLAM | Priority: P1
> Depends on: PRD-03
> Status: ⬜ Not started

## Objective
Integrate the online MipSLAM pipeline into ANIMA’s ROS2 environment so a ZED 2i RGB-D stream can drive real-time tracking, mapping, and alias-free rendering diagnostics.

## Context (from paper)
MipSLAM is an RGB-D SLAM system. For ANIMA, the direct hardware translation is a ROS2 node that subscribes to synchronized RGB, depth, and camera calibration topics and publishes poses plus rendering outputs.

**Paper reference**: Fig. 2, Sec. III, Sec. IV-A

## Acceptance Criteria
- [ ] ROS2 node consumes synchronized RGB image, depth image, and `CameraInfo`.
- [ ] Node publishes `PoseStamped`, `Path`, and optional rendered preview images.
- [ ] Launch file supports offline bag replay and live sensor execution.
- [ ] Diagnostics topic exposes keyframe count, SA-PGO status, render latency, and spectral gap.
- [ ] Test: `uv run pytest tests/test_ros2_adapter.py -v` passes.

## Files to Create
| File | Purpose | Paper Ref | Est. Lines |
|------|---------|-----------|-----------|
| `src/anima_slam_mipslam/ros2/node.py` | ROS2 runtime wrapper | Fig. 2 | ~220 |
| `src/anima_slam_mipslam/ros2/conversions.py` | ROS image / depth / pose conversions | Sec. III | ~140 |
| `src/anima_slam_mipslam/ros2/launch/mipslam.launch.py` | Launch config for offline and live runs | — | ~90 |
| `tests/test_ros2_adapter.py` | ROS adapter unit tests | — | ~100 |

## Architecture Detail (from paper)
### Inputs
- `/zed/rgb/image_rect_color`
- `/zed/depth/depth_registered`
- `/zed/rgb/camera_info`

### Outputs
- `/mipslam/pose`
- `/mipslam/path`
- `/mipslam/render/rgb`
- `/mipslam/render/depth`
- `/mipslam/diagnostics`

### Algorithm
```python
class MipSLAMNode(Node):
    def on_frame(self, rgb_msg, depth_msg, camera_info_msg):
        frame = ros_to_frame_batch(rgb_msg, depth_msg, camera_info_msg)
        pose, render = self.pipeline.step(frame)
        self.publish_outputs(pose, render)
```

## Dependencies
```toml
rclpy = "ROS2 runtime"
sensor_msgs = "ROS2 runtime"
geometry_msgs = "ROS2 runtime"
nav_msgs = "ROS2 runtime"
```

## Data Requirements
| Asset | Size | Path | Download |
|-------|------|------|----------|
| ROS2 RGB-D bag or live sensor stream | runtime input | Sensor / bag storage | External |

## Test Plan
```bash
uv run pytest tests/test_ros2_adapter.py -v
```

## References
- Paper: Fig. 2, Sec. III, Sec. IV-A
- Depends on: PRD-03
- Feeds into: PRD-07
