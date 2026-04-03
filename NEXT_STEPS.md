# SLAM-MIPSLAM — Execution Ledger

Resume rule: Read this file COMPLETELY before writing any code.
This project covers exactly ONE paper: MipSLAM: Alias-Free Gaussian Splatting SLAM.

## 1. Working Rules
- Work only inside `project_slam_mipslam/`
- This wave has 17 parallel projects, 17 papers, 17 agents
- Prefix every commit with `[SLAM-MIPSLAM]`
- Stage only `project_slam_mipslam/` files
- VERIFY THE PAPER BEFORE BUILDING ANYTHING

## 2. The Paper
- **Title**: MipSLAM: Alias-Free Gaussian Splatting SLAM
- **ArXiv**: 2603.06989
- **Link**: https://arxiv.org/abs/2603.06989
- **Repo**: https://github.com/yzli1998/MipSLAM
- **Compute**: GPU-NEED
- **Verification status**: ArXiv ID ✅ | Repo ✅ | Paper read ✅ | Repo code release empty ⚠️

## 3. Current Status
- **Date**: 2026-04-03
- **Phase**: PRD-02 preparation
- **MVP Readiness**: 20%
- **Accomplished**:
  1. Correct paper identified and downloaded locally
  2. `ASSETS.md`, `PIPELINE_MAP.md`, `prds/`, and `tasks/` generated
  3. Top-level `PRD.md` rewritten around the actual paper
  4. PRD-01 foundation implemented and validated on Python 3.11 with UV
  5. Missing infra files created: `anima_module.yaml`, `Dockerfile.serve`, `docker-compose.serve.yml`, `serve.py`
- **TODO**:
  1. Start PRD-02 task `PRD-0201` incremental 3D filter
  2. Start PRD-02 task `PRD-0202` elliptical-domain sampling
  3. Download or mount Replica / TUM RGB-D benchmark sequences
  4. Decide whether to mirror MonoGS/SplaTAM defaults for omitted hyperparameters
- **Blockers**:
  1. Training remains blocked until Replica and TUM RGB-D are available locally or on the target CUDA host

## 4. Datasets
### Required for this paper
| Dataset | Size | URL | Format | Phase Needed |
|---------|------|-----|--------|-------------|
| Replica | 8 eval sequences | https://github.com/facebookresearch/Replica-Dataset | RGB-D frames + poses | Phase 4 |
| TUM RGB-D | 3 eval sequences | https://cvg.cit.tum.de/data/datasets/rgbd-dataset | RGB-D frames + associations | Phase 4 |

### Check shared volume first
/Volumes/AIFlowDev/RobotFlowLabs/datasets

### Download
`bash scripts/download_data.sh`

## 5. Hardware
- ZED 2i stereo camera: Available
- Unitree L2 3D LiDAR: Available
- xArm 6 cobot: Pending purchase
- Mac Studio M-series: MLX dev
- 8x RTX 6000 Pro Blackwell: GCloud

## 6. Session Log
| Date | Agent | What Happened |
|------|-------|---------------|
| 2026-04-03 | ANIMA Research Agent | Project scaffolded |
| 2026-04-03 | Codex | Corrected paper source to arXiv 2603.06989 and generated PRD / task suite |
| 2026-04-03 | Codex | Completed PRD-01 foundation prebuild, UV 3.11 environment, and infra scaffolding |
