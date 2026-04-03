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
- **Phase**: Planning
- **MVP Readiness**: 12%
- **Accomplished**:
  1. Correct paper identified and downloaded locally
  2. `ASSETS.md`, `PIPELINE_MAP.md`, `prds/`, and `tasks/` generated
  3. Top-level `PRD.md` rewritten around the actual paper
- **TODO**:
  1. Implement PRD-01 foundation tasks
  2. Download or mount Replica / TUM RGB-D benchmark sequences
  3. Decide whether to mirror MonoGS/SplaTAM defaults for omitted hyperparameters
  4. Start PRD-02 EAA and SA-PGO core implementation
- **Blockers**: None

## 4. Datasets
### Required for this paper
| Dataset | Size | URL | Format | Phase Needed |
|---------|------|-----|--------|-------------|
| (TODO after reading paper) | — | — | — | Phase 1 |

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
