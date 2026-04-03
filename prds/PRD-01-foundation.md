# PRD-01: Foundation And Data Contracts

> Module: SLAM-MIPSLAM | Priority: P0
> Depends on: None
> Status: ✅ Done

## Objective
Establish the canonical package layout, configuration system, RGB-D dataset adapters, and Gaussian/pose data contracts needed to implement MipSLAM faithfully.

## Context (from paper)
MipSLAM is built around three modules: tracking, alias-free Gaussian mapping, and frequency-domain pose graph optimization. The paper assumes RGB-D input, a global Gaussian map, and repeated rendering under varying camera resolutions.

**Paper reference**: Sec. III, Fig. 2, Sec. IV-A

## Acceptance Criteria
- [ ] Canonical package path `src/anima_slam_mipslam/` exists and replaces the placeholder scaffold.
- [ ] Replica and TUM RGB-D adapters emit RGB, depth, intrinsics, and optional pose ground truth in one typed sample object.
- [ ] Gaussian primitive, keyframe, and pose-graph dataclasses cover the variables used in Sec. III-A through III-D.
- [ ] Resolution sweep config supports Replica `2x/1x/1/2/1/4/1/8` and TUM `4x/2x/1x/1/2/1/4`.
- [ ] Test: `uv run pytest tests/test_config.py tests/test_datasets.py tests/test_geometry.py -v` passes.

## Files to Create
| File | Purpose | Paper Ref | Est. Lines |
|------|---------|-----------|-----------|
| `src/anima_slam_mipslam/config.py` | Pydantic settings and typed experiment config | Sec. IV-A | ~180 |
| `src/anima_slam_mipslam/data/replica.py` | Replica sequence loader and scaler | Sec. IV-A | ~220 |
| `src/anima_slam_mipslam/data/tum_rgbd.py` | TUM RGB-D loader and scaler | Sec. IV-A | ~220 |
| `src/anima_slam_mipslam/gaussians/types.py` | Gaussian state, camera, pose graph dataclasses | Sec. III-A | ~180 |
| `tests/test_config.py` | Config validation | — | ~80 |
| `tests/test_datasets.py` | Dataset shape / scale tests | — | ~120 |
| `tests/test_geometry.py` | Basic camera / projection invariants | — | ~120 |

## Architecture Detail (from paper)
### Inputs
- `rgb`: `Tensor[H,W,3]` in `float32`
- `depth`: `Tensor[H,W]` in meters
- `K`: `Tensor[3,3]` camera intrinsics
- `T_wc`: `Tensor[4,4]` camera pose when available

### Outputs
- `FrameBatch`: RGB-D frame plus calibrated camera metadata
- `GaussianMapState`: arrays for `mu`, `Sigma`, `alpha`, `sh_coeffs`
- `PoseGraphState`: nodes, edges, edge weights, spectral metadata

### Algorithm
```python
# Paper refs: Fig. 2, Sec. III-A, Sec. IV-A

class FrameBatch:
    rgb: torch.Tensor        # [H, W, 3]
    depth: torch.Tensor      # [H, W]
    intrinsics: torch.Tensor # [3, 3]
    pose: torch.Tensor | None


class GaussianPrimitive:
    mean: torch.Tensor       # [3]
    covariance: torch.Tensor # [3, 3]
    opacity: torch.Tensor    # [1]
    sh_coeffs: torch.Tensor  # [C_sh, 3]
```

## Dependencies
```toml
numpy = ">=2.0"
torch = ">=2.3"
pydantic = ">=2.8"
opencv-python = ">=4.10"
```

## Data Requirements
| Asset | Size | Path | Download |
|-------|------|------|----------|
| Replica sequences used in paper | 8 eval sequences | `/Volumes/AIFlowDev/RobotFlowLabs/datasets/replica/` | External dataset |
| TUM RGB-D sequences used in paper | 3 eval sequences | `/Volumes/AIFlowDev/RobotFlowLabs/datasets/tum_rgbd/` | External dataset |

## Test Plan
```bash
uv run pytest tests/test_config.py tests/test_datasets.py tests/test_geometry.py -v
```

## References
- Paper: Sec. III, Fig. 2, Sec. IV-A
- Depends on: None
- Feeds into: PRD-02, PRD-03, PRD-04
