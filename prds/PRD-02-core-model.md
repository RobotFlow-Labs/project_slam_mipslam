# PRD-02: Core Alias-Free Mapping And SA-PGO

> Module: SLAM-MIPSLAM | Priority: P0
> Depends on: PRD-01
> Status: ✅ Completed

## Objective
Implement the two paper-novel cores of MipSLAM: Elliptical Adaptive Anti-aliasing (EAA) for Gaussian rendering and Spectral-Aware Pose Graph Optimization (SA-PGO) for drift suppression.

## Context (from paper)
The paper’s contribution is not generic 3DGS SLAM. It specifically replaces point-sampled Gaussian projection with elliptical numerical integration and augments pose graph optimization with frequency-aware spectral analysis.

**Paper reference**: Sec. III-A, Sec. III-B, Sec. III-C, Eq. (1)-(15)

## Acceptance Criteria
- [x] Gaussian rendering uses integrated opacity from Eq. (6), not vanilla point sampling.
- [x] Incremental 3D filter from Eq. (3) updates per-Gaussian frequency support from active keyframes.
- [x] EAA sampling implements geometry- and boundary-aware importance weights from Eq. (5).
- [x] SA-PGO computes descriptors, spectral signatures, graph Laplacian decomposition, and the optimization objective from Eq. (8)-(14).
- [x] Joint training loss matches Eq. (15) with RGB and depth terms.
- [x] Test: `uv run pytest tests/test_eaa_renderer.py tests/test_sa_pgo.py tests/test_losses.py -v` passes.

## Files to Create
| File | Purpose | Paper Ref | Est. Lines |
|------|---------|-----------|-----------|
| `src/anima_slam_mipslam/render/eaa_sampling.py` | Elliptical-domain quadrature point generation | Sec. III-B.2 | ~220 |
| `src/anima_slam_mipslam/render/eaa_renderer.py` | Integrated-opacity Gaussian renderer | Eq. (6), Sec. III-B.3 | ~260 |
| `src/anima_slam_mipslam/mapping/filter3d.py` | Sliding-window 3D filter update | Eq. (3), Sec. III-B.1 | ~140 |
| `src/anima_slam_mipslam/backend/descriptors.py` | FFT / gradient / texture / color descriptors | Eq. (8), Sec. III-C.1 | ~180 |
| `src/anima_slam_mipslam/backend/sa_pgo.py` | Spectral confidence, Laplacian, optimization | Eq. (9)-(14), Sec. III-C | ~280 |
| `src/anima_slam_mipslam/training/losses.py` | RGB-depth joint loss | Eq. (15), Sec. III-D | ~120 |
| `tests/test_eaa_renderer.py` | EAA numerical correctness tests | — | ~140 |
| `tests/test_sa_pgo.py` | Spectral pose graph tests | — | ~140 |
| `tests/test_losses.py` | Joint loss tests | — | ~80 |

## Architecture Detail (from paper)
### Inputs
- `gaussians.mean`: `Tensor[N,3]`
- `gaussians.covariance`: `Tensor[N,3,3]`
- `gaussians.opacity`: `Tensor[N,1]`
- `gaussians.sh_coeffs`: `Tensor[N,C_sh,3]`
- `trajectory_window`: `Tensor[N_w,6]`
- `render_query`: camera pose `Tensor[4,4]`, intrinsics `Tensor[3,3]`, resolution `(H, W)`

### Outputs
- `rgb_render`: `Tensor[H,W,3]`
- `depth_render`: `Tensor[H,W]`
- `alpha_render`: `Tensor[H,W]`
- `spectral_confidence`: `Tensor[E]`
- `pose_updates`: `Tensor[T,4,4]`

### Algorithm
```python
# Paper refs: Eq. (3)-(15)

class EAARenderer(nn.Module):
    def forward(self, gaussians, camera):
        proj = project_gaussians_to_image(gaussians, camera)
        samples, weights = sample_elliptical_domain(proj)
        alpha = integrate_opacity(samples, weights, proj)
        return alpha_blend_rgbd(alpha, proj)


class SpectralAwarePGO(nn.Module):
    def forward(self, poses, descriptors, pose_graph):
        spectral = compute_frequency_signatures(poses)
        adjacency = build_spectral_adjacency(descriptors, spectral, pose_graph)
        return optimize_pose_graph(poses, adjacency)
```

## Dependencies
```toml
torch = ">=2.3"
scipy = ">=1.13"
networkx = ">=3.3"
```

## Data Requirements
| Asset | Size | Path | Download |
|-------|------|------|----------|
| Sample Replica clip for renderer tests | short clip | `/Volumes/AIFlowDev/RobotFlowLabs/datasets/replica/` | External dataset |
| Sample TUM clip for pose graph tests | short clip | `/Volumes/AIFlowDev/RobotFlowLabs/datasets/tum_rgbd/` | External dataset |

## Test Plan
```bash
uv run pytest tests/test_eaa_renderer.py tests/test_sa_pgo.py tests/test_losses.py -v
```

## References
- Paper: Sec. III-A through III-D
- Depends on: PRD-01
- Feeds into: PRD-03, PRD-04
