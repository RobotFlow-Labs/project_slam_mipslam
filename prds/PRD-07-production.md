# PRD-07: Production Hardening And Release Validation

> Module: SLAM-MIPSLAM | Priority: P1
> Depends on: PRD-04, PRD-05, PRD-06
> Status: ⬜ Not started

## Objective
Harden the MipSLAM implementation for repeatable ANIMA deployment with validated benchmarks, runtime profiling, artifact export, and clear fallback behavior when paper-disclosed parameters are incomplete.

## Context (from paper)
The paper provides strong benchmark targets but omits several engineering details and ships no usable code. Productionization must freeze the recovered configuration, capture evaluation deltas against the paper, and define operational limits for real-time use.

**Paper reference**: Abstract, Sec. IV, Sec. V

## Acceptance Criteria
- [ ] Release bundle includes map checkpoints, configs, eval reports, and API/ROS2 launch instructions.
- [ ] Runtime profiling captures render latency, SA-PGO cadence, GPU memory, and fallback conditions.
- [ ] Degradation strategy is defined for insufficient compute, unsupported camera changes, or missing depth.
- [ ] Final validation compares implementation output against Tables I-III and documents any gap.
- [ ] Test: `uv run pytest tests/test_release_bundle.py tests/test_runtime_limits.py -v` passes.

## Files to Create
| File | Purpose | Paper Ref | Est. Lines |
|------|---------|-----------|-----------|
| `configs/prod/runtime.toml` | Production runtime guardrails | Sec. IV-V | ~100 |
| `scripts/profile_mipslam.py` | Runtime profiling harness | Sec. IV | ~180 |
| `scripts/package_release.py` | Bundle checkpoints, configs, and reports | — | ~140 |
| `tests/test_release_bundle.py` | Release bundle tests | — | ~100 |
| `tests/test_runtime_limits.py` | Runtime guardrail tests | — | ~100 |
| `reports/production_validation_template.md` | Final signoff template | Sec. V | ~80 |

## Architecture Detail (from paper)
### Inputs
- Benchmarked checkpoint directory
- Evaluation reports from PRD-04
- API and ROS2 configs from PRD-05 / PRD-06

### Outputs
- Versioned release bundle
- Runtime profile JSON / Markdown
- Production validation report

### Algorithm
```python
def build_release_bundle(run_dir: Path) -> Path:
    assert benchmark_report_exists(run_dir)
    assert api_smoke_test_passed(run_dir)
    return package_artifacts(run_dir)
```

## Dependencies
```toml
psutil = ">=6.0"
rich = ">=13.7"
```

## Data Requirements
| Asset | Size | Path | Download |
|-------|------|------|----------|
| Final checkpoints and reports | generated artifact | `artifacts/mipslam/` | Built in prior PRDs |

## Test Plan
```bash
uv run pytest tests/test_release_bundle.py tests/test_runtime_limits.py -v
```

## References
- Paper: Abstract, Sec. IV, Sec. V
- Depends on: PRD-04, PRD-05, PRD-06
- Feeds into: final module release
