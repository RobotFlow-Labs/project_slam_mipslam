# PRD-04: Evaluation And Paper Reproduction

> Module: SLAM-MIPSLAM | Priority: P0
> Depends on: PRD-01, PRD-02, PRD-03
> Status: ⬜ Not started

## Objective
Reproduce the paper’s multi-resolution rendering and localization results on Replica and TUM RGB-D, and emit a structured comparison report against the paper tables.

## Context (from paper)
The paper’s claims are entirely benchmark-driven: Tables I and II measure PSNR, SSIM, and LPIPS under resolution changes, while Table III measures ATE RMSE on Replica. The implementation is not complete until these tables can be regenerated.

**Paper reference**: Sec. IV-A, Sec. IV-B, Sec. IV-C, Tables I-III

## Acceptance Criteria
- [ ] Evaluation harness reproduces Replica scales `2x/1x/1/2/1/4/1/8`.
- [ ] Evaluation harness reproduces TUM scales `4x/2x/1x/1/2/1/4`.
- [ ] Report contains Replica average target `PSNR 35.83`, `SSIM 0.959`, `LPIPS 0.048`.
- [ ] Report contains TUM average target `PSNR 22.77`, `SSIM 0.810`, `LPIPS 0.220`.
- [ ] Localization report contains Replica target `ATE RMSE 0.28 cm`.
- [ ] Test: `uv run pytest tests/test_eval_metrics.py tests/test_eval_protocol.py -v` passes.

## Files to Create
| File | Purpose | Paper Ref | Est. Lines |
|------|---------|-----------|-----------|
| `src/anima_slam_mipslam/eval/render_metrics.py` | PSNR, SSIM, LPIPS across resolution sweeps | Tables I-II | ~200 |
| `src/anima_slam_mipslam/eval/localization.py` | ATE RMSE and trajectory alignment | Table III | ~180 |
| `src/anima_slam_mipslam/eval/report.py` | Markdown/JSON reproduction report | Sec. IV | ~180 |
| `configs/eval/replica.toml` | Replica eval protocol | Sec. IV-A | ~80 |
| `configs/eval/tum.toml` | TUM eval protocol | Sec. IV-A | ~80 |
| `tests/test_eval_metrics.py` | Metric correctness | — | ~120 |
| `tests/test_eval_protocol.py` | Protocol / table generation tests | — | ~120 |

## Architecture Detail (from paper)
### Inputs
- `render_results`: rendered RGB/depth frames and GT
- `trajectory_results`: predicted pose list and GT pose list
- `dataset_name`: `replica` or `tum_rgbd`

### Outputs
- `metrics_table`: structured rows for all scales
- `ate_report`: per-scene and average localization metrics
- `reproduction_report.md`: paper vs. implementation delta summary

### Algorithm
```python
# Paper refs: Sec. IV, Tables I-III

def evaluate_multiresolution(run_dir, dataset_cfg):
    for scale in dataset_cfg.scales:
        renders = render_checkpoint_at_scale(run_dir, scale)
        metrics[scale] = compute_render_metrics(renders)
    return metrics
```

## Dependencies
```toml
torchmetrics = ">=1.4"
lpips = ">=0.1.4"
numpy = ">=2.0"
```

## Data Requirements
| Asset | Size | Path | Download |
|-------|------|------|----------|
| Replica benchmark scenes | 8 sequences | `/Volumes/AIFlowDev/RobotFlowLabs/datasets/replica/` | External dataset |
| TUM benchmark scenes | 3 sequences | `/Volumes/AIFlowDev/RobotFlowLabs/datasets/tum_rgbd/` | External dataset |

## Test Plan
```bash
uv run pytest tests/test_eval_metrics.py tests/test_eval_protocol.py -v
```

## References
- Paper: Sec. IV-A through IV-C, Tables I-III
- Depends on: PRD-01, PRD-02, PRD-03
- Feeds into: PRD-07
