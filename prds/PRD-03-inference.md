# PRD-03: Online SLAM Inference

> Module: SLAM-MIPSLAM | Priority: P0
> Depends on: PRD-01, PRD-02
> Status: ◐ In progress

## Objective
Build the online RGB-D SLAM loop that tracks, updates the Gaussian map, periodically runs SA-PGO, and re-renders the map under arbitrary camera resolutions and intrinsics.

## Context (from paper)
Fig. 2 describes a pipeline where MipSLAM tracks RGB-D streams, selects keyframes, updates Gaussian maps in a sliding window, and refines poses asynchronously through SA-PGO. The system is evaluated under changed camera configurations, so inference must support map reuse across resolutions.

**Paper reference**: Fig. 2, Sec. III, Sec. IV-A

## Acceptance Criteria
- [x] Online loop ingests sequential RGB-D frames and maintains a keyframe database plus covisibility graph.
- [x] Tracking path produces per-frame poses and rendered RGB-depth supervision for map updates.
- [ ] Backend runs SA-PGO asynchronously and feeds refined poses back into the map state.
- [x] Saved map can be re-rendered at Replica and TUM evaluation scales without changing scene content.
- [x] CLI entry supports `run-sequence`, `render-map`, and `export-trajectory`.
- [x] Test: `uv run pytest tests/test_online_slam.py tests/test_render_reuse.py -v` passes.

## Files to Create
| File | Purpose | Paper Ref | Est. Lines |
|------|---------|-----------|-----------|
| `src/anima_slam_mipslam/tracking/frontend.py` | Frame-to-map tracking loop | Fig. 2, Sec. III | ~220 |
| `src/anima_slam_mipslam/mapping/backend.py` | Keyframe DB, covisibility, async optimization | Fig. 2, Sec. III | ~240 |
| `src/anima_slam_mipslam/pipeline/online_slam.py` | Orchestrates tracking, mapping, SA-PGO | Fig. 2 | ~260 |
| `src/anima_slam_mipslam/cli/run_slam.py` | CLI for sequence runs and rendering | Sec. IV-A | ~140 |
| `tests/test_online_slam.py` | Stream-level smoke tests | — | ~120 |
| `tests/test_render_reuse.py` | Resolution / intrinsic reuse tests | — | ~120 |

## Architecture Detail (from paper)
### Inputs
- `stream`: iterable of `FrameBatch`
- `map_state`: `GaussianMapState`
- `config`: tracking, mapping, and SA-PGO settings

### Outputs
- `trajectory`: `Tensor[T,4,4]`
- `map_checkpoint`: serialized Gaussian map and metadata
- `rendered_rgb`: `Tensor[H,W,3]`
- `rendered_depth`: `Tensor[H,W]`

### Algorithm
```python
# Paper refs: Fig. 2, Eq. (3)-(15)

class OnlineMipSLAM:
    def run(self, stream):
        for frame in stream:
            pose = self.frontend.track(frame, self.map_state)
            self.backend.update(frame, pose, self.map_state)
            if self.backend.should_run_sa_pgo():
                self.poses = self.sa_pgo(self.poses, self.backend.pose_graph)
        return self.poses, self.map_state
```

## Dependencies
```toml
torch = ">=2.3"
typer = ">=0.12"
tqdm = ">=4.66"
```

## Data Requirements
| Asset | Size | Path | Download |
|-------|------|------|----------|
| Replica smoke-test scene | 1 sequence | `/Volumes/AIFlowDev/RobotFlowLabs/datasets/replica/` | External dataset |
| TUM smoke-test scene | 1 sequence | `/Volumes/AIFlowDev/RobotFlowLabs/datasets/tum_rgbd/` | External dataset |

## Test Plan
```bash
uv run pytest tests/test_online_slam.py tests/test_render_reuse.py -v
```

## References
- Paper: Fig. 2, Sec. III, Sec. IV-A
- Depends on: PRD-01, PRD-02
- Feeds into: PRD-04, PRD-05, PRD-06
