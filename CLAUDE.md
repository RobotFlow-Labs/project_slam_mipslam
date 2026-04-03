# SLAM-MIPSLAM

## Paper
**MipSLAM: Alias-Free Gaussian Splatting SLAM**
arXiv: https://arxiv.org/abs/2603.06989

## Module Identity
- Codename: SLAM-MIPSLAM
- Domain: SLAM
- Part of ANIMA Intelligence Compiler Suite
- Source note: official GitHub repo exists but was empty when this project was scaffolded

## Structure
```
project_slam_mipslam/
├── pyproject.toml
├── configs/
├── src/anima_slam_mipslam/
├── tests/
├── scripts/
├── papers/          # Paper PDF
├── CLAUDE.md        # This file
├── NEXT_STEPS.md
├── ASSETS.md
└── PRD.md
```

## Commands
```bash
uv sync
uv run pytest
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

## Conventions
- Package manager: uv (never pip)
- Build backend: hatchling
- Python: >=3.10
- Config: TOML + Pydantic BaseSettings
- Lint: ruff
- Git commit prefix: [SLAM-MIPSLAM]
