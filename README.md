# SLAM-MIPSLAM — ANIMA Module

> **MipSLAM: Alias-Free Gaussian Splatting SLAM**
> Paper: [arXiv:2603.06989](https://arxiv.org/abs/2603.06989)

Part of the [ANIMA Intelligence Compiler Suite](https://github.com/RobotFlow-Labs) by AIFLOW LABS LIMITED.

## Domain
SLAM

## Status
- [x] Paper read + ASSETS.md created
- [x] PRD-01 through PRD-07
- [x] Granular `tasks/` created
- [ ] Training pipeline
- [ ] GPU training
- [ ] Export: pth + safetensors + ONNX + TRT fp16 + TRT fp32
- [ ] Push to HuggingFace
- [ ] Docker serving

## Quick Start
```bash
cd project_slam_mipslam
uv venv .venv --python python3.11
uv sync --extra dev --extra serve
uv run pytest tests/test_config.py tests/test_datasets.py tests/test_geometry.py -v
uv run python -m anima_slam_mipslam
```

## Runtime Notes
- macOS prebuild path: MLX / MPS / CPU capable via `ANIMA_BACKEND=auto`
- later CUDA path: `uv sync --extra dev --extra serve --extra cuda` on Linux GPU hosts
- current training blocker: Replica and TUM RGB-D datasets are not mounted locally yet

## License
MIT — AIFLOW LABS LIMITED
