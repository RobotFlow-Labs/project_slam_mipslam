# MipSLAM Pipeline Map

This document maps the paper components in `MipSLAM: Alias-Free Gaussian Splatting SLAM` to the implementation plan for this module.

## Source Correction
- Correct paper: `2603.06989`
- Stale scaffold reference: `2503.15908`
- Official repo status: present but empty, so implementation must follow the paper equations and diagrams directly.

## Paper-To-Code Mapping
| Paper Component | Paper Ref | What It Does | Planned Code Surface | Inputs | Outputs | Owning PRD |
|----------------|-----------|--------------|----------------------|--------|---------|------------|
| RGB-D stream ingestion | Fig. 2, Sec. III | Accepts RGB-D frames, intrinsics, poses | `src/anima_slam_mipslam/data/` | RGB `Tensor[H,W,3]`, depth `Tensor[H,W]`, intrinsics `Tensor[3,3]` | `FrameBatch`, `KeyframeRecord` | PRD-01 |
| Gaussian state representation | Sec. III-A, Eqs. (1)-(2) | Stores anisotropic 3D Gaussians, SH appearance, opacity | `src/anima_slam_mipslam/gaussians/state.py` | `mu_i`, `Sigma_i`, `alpha_i`, `c_i` | `GaussianMapState` | PRD-01, PRD-02 |
| Incremental 3D filter | Sec. III-B.1, Eq. (3) | Tracks maximum sampling frequency from active keyframes | `src/anima_slam_mipslam/mapping/filter3d.py` | Active keyframes, focal length, Gaussian depth | Updated `nu_hat` per Gaussian | PRD-02 |
| EAA elliptical sampling | Sec. III-B.2, Eq. (5) | Samples in Gaussian principal-axis space with geometry-aware weights | `src/anima_slam_mipslam/render/eaa_sampling.py` | Projected mean/covariance, boundary distances | Quadrature points and weights | PRD-02 |
| Numerical integration renderer | Sec. III-B.3, Eq. (6) | Replaces point-sampled alpha with integrated opacity | `src/anima_slam_mipslam/render/eaa_renderer.py` | Gaussian set, camera, pixel footprint | Alias-free alpha, RGB, depth | PRD-02, PRD-03 |
| Gradient path for EAA | Sec. III-B.4, Eq. (7) | Keeps backward pass consistent with numerical integration | `src/anima_slam_mipslam/render/autograd.py` | EAA intermediates | Gradients for map optimization | PRD-02 |
| Multi-modal trajectory descriptors | Sec. III-C.1, Eq. (8) | Extracts FFT, gradient, texture, color features | `src/anima_slam_mipslam/backend/descriptors.py` | Rendered / observed images and trajectory snippets | Descriptor vectors `d_i` | PRD-02 |
| Frequency-domain trajectory analysis | Sec. III-C.2, Eqs. (9)-(12) | Computes spectral signatures, coherence, confidence | `src/anima_slam_mipslam/backend/frequency.py` | Pose window `Tensor[N_w,6]` | `S_k`, `C_ij`, `S_ij` | PRD-02 |
| Graph Laplacian + SA-PGO | Sec. III-C.3-.4, Eqs. (13)-(14) | Reweights and optimizes pose graph using spectral structure | `src/anima_slam_mipslam/backend/sa_pgo.py` | Pose graph, spectral confidences, descriptors | Refined poses `x*` | PRD-02, PRD-03 |
| Joint photometric-depth training | Sec. III-D, Eq. (15) | Co-optimizes camera poses and Gaussian parameters | `src/anima_slam_mipslam/training/losses.py` | Rendered RGB/depth and GT RGB/depth | Scalar loss, gradients | PRD-02, PRD-03 |
| Online tracking + mapping loop | Fig. 2, Sec. III / IV | Runs front-end tracking and map updates asynchronously with SA-PGO | `src/anima_slam_mipslam/pipeline/online_slam.py` | Frame stream + config | Pose trajectory + Gaussian map | PRD-03 |
| Multi-resolution evaluation | Sec. IV, Tables I-III | Reproduces rendering and localization metrics across resolution sweeps | `src/anima_slam_mipslam/eval/` | Saved maps, trajectories, dataset splits | PSNR/SSIM/LPIPS/FPS/ATE reports | PRD-04 |
| API / Docker serving | Paper motivation + ANIMA requirement | Builds map once, relocalizes and renders under changed camera configs | `src/anima_slam_mipslam/api/`, `docker/` | Map checkpoint, query camera params | Rendered image, depth, pose estimate | PRD-05 |
| ROS2 runtime bridge | ANIMA adaptation | Connects RGB-D sensors and publishes real-time outputs | `ros2/` or `src/anima_slam_mipslam/ros2/` | ROS image/depth/camera topics | Pose, render, diagnostics topics | PRD-06 |
| Production hardening | Post-paper deployment | Profiles runtime, validates degradation paths, packages artifacts | `scripts/`, `configs/prod/`, release docs | Bench results + checkpoints | Release bundle + validation report | PRD-07 |

## Execution Notes
- The paper is RGB-D only. ZED 2i is the direct hardware fit; Unitree L2 LiDAR belongs to later ANIMA fusion work, not the paper-faithful baseline.
- Because the official repo is empty, PRD-02 must preserve the equations and terminology from Sec. III instead of borrowing undocumented behavior from unrelated 3DGS SLAM implementations.
- The current source tree contains placeholder files under `src/anima_susanoo/`; PRD-01 converts that scaffold into the canonical `src/anima_slam_mipslam/` layout while keeping a temporary compatibility shim if needed.
