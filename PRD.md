# SLAM-MIPSLAM: MipSLAM — Implementation PRD
## ANIMA Wave-7 Module

**Status:** PRD suite generated
**Version:** 0.2
**Date:** 2026-04-03
**Paper:** MipSLAM: Alias-Free Gaussian Splatting SLAM
**Paper Link:** https://arxiv.org/abs/2603.06989
**Repo:** https://github.com/yzli1998/MipSLAM
**Repo Status:** Empty repository as of 2026-04-03
**Functional Name:** SLAM-mipslam
**Stack:** PHANTOMAGIA

## 1. Executive Summary
MipSLAM is a paper-driven RGB-D 3D Gaussian Splatting SLAM system whose novelty comes from two additions to the normal 3DGS SLAM pipeline: Elliptical Adaptive Anti-aliasing (EAA) for alias-free rendering under changed camera configurations and Spectral-Aware Pose Graph Optimization (SA-PGO) for reducing trajectory drift. This module should reproduce the paper faithfully before any ANIMA-specific extensions.

## 2. Paper Verification Status
- [x] Correct paper identified as `arXiv:2603.06989`
- [x] Paper read completely
- [x] Official GitHub repository checked
- [x] Empty official repo noted as implementation risk
- [ ] Datasets confirmed present on shared volume
- [ ] Paper metrics reproduced locally
- [ ] Real-time ANIMA integration validated
- **Verdict:** Proceed with paper-faithful implementation from the paper text; do not rely on the empty upstream repo.

## 3. What We Take From The Paper
- Alias-free Gaussian rendering via EAA, especially the incremental 3D filter, elliptical-domain sampling, and numerical integration pipeline in Sec. III-B.
- SA-PGO exactly as described in Sec. III-C, including multi-modal descriptors, sliding-window DFT, graph Laplacian decomposition, and spectral regularization.
- RGB-depth joint optimization in Eq. (15).
- Benchmark protocol from Sec. IV on Replica and TUM RGB-D with multiresolution evaluation.

## 4. What We Skip
- Any undocumented behavior that would require reverse-engineering missing source code.
- Non-RGB-D sensor fusion in the first reproduction pass.
- Paper-extraneous features such as LiDAR fusion, semantic mapping, or learned priors not described in Sec. III-IV.

## 5. What We Adapt
- ANIMA packaging, API surface, Dockerization, and ROS2 integration.
- ZED 2i RGB-D ingestion as the hardware-aligned runtime path.
- Explicit fallback and profiling infrastructure, because the paper does not publish engineering guardrails.

## 6. Architecture
The implementation will be split into seven PRDs:
- Foundation and data contracts
- Core EAA and SA-PGO model logic
- Online RGB-D SLAM inference
- Evaluation and paper reproduction
- API and Docker packaging
- ROS2 runtime bridge
- Production hardening and release validation

## 7. Implementation Phases

### Phase 1 — Foundation + Paper Recovery
- [x] Correct package layout and configs
- [x] Dataset loaders for Replica and TUM RGB-D
- [x] Gaussian / pose graph typed state
- [ ] Resolve missing hyperparameters with documented inferred defaults

### Phase 2 — Core Method
- [ ] EAA renderer from Sec. III-B
- [ ] SA-PGO backend from Sec. III-C
- [ ] Joint RGB-depth loss from Eq. (15)

### Phase 3 — Online System
- [ ] Tracking and mapping loop
- [ ] Map reuse across changed resolutions and intrinsics
- [ ] Artifact export and CLI entrypoints

### Phase 4 — Reproduction + Integration
- [ ] Benchmark on Replica and TUM RGB-D
- [ ] API and Docker
- [ ] ROS2 runtime node
- [ ] Production validation report

## 8. Datasets
| Dataset | Source | Protocol |
|---------|--------|----------|
| Replica | https://github.com/facebookresearch/Replica-Dataset | 8 sequences, scales `2x/1x/1/2/1/4/1/8` |
| TUM RGB-D | https://cvg.cit.tum.de/data/datasets/rgbd-dataset | 3 sequences, scales `4x/2x/1x/1/2/1/4` |

## 9. Dependencies On Other Wave Projects
| Needs output from | What it provides |
|------------------|------------------|
| None required for paper-faithful baseline | — |

## 10. Success Criteria
- Replica average: `PSNR >= 35.0`, `SSIM >= 0.950`, `LPIPS <= 0.060`
- TUM average: `PSNR >= 22.0`, `SSIM >= 0.790`, `LPIPS <= 0.240`
- Replica localization average: `ATE RMSE <= 0.35 cm`
- Stable re-rendering under changed camera resolutions without the aliasing failure modes highlighted in Figs. 4-5

## 11. Risk Assessment
- The official repo is empty, so all recovery depends on paper fidelity.
- Several numerical hyperparameters are omitted, creating reproduction risk.
- The current scaffold still contains stale metadata and placeholder package naming.
- Real-time performance from the paper’s RTX 4090 environment may not transfer directly to every ANIMA target.

## 12. Build Plan
| PRD | Task | Status |
|-----|------|--------|
| [PRD-01](prds/PRD-01-foundation.md) | Foundation and data contracts | ✅ |
| [PRD-02](prds/PRD-02-core-model.md) | EAA renderer, SA-PGO, losses | ✅ |
| [PRD-03](prds/PRD-03-inference.md) | Online SLAM inference loop | ◐ |
| [PRD-04](prds/PRD-04-evaluation.md) | Reproduction benchmarks and reports | ⬜ |
| [PRD-05](prds/PRD-05-api-docker.md) | API and Docker packaging | ⬜ |
| [PRD-06](prds/PRD-06-ros2-integration.md) | ROS2 runtime bridge | ⬜ |
| [PRD-07](prds/PRD-07-production.md) | Production hardening and validation | ⬜ |

## 13. Supporting Docs
- [ASSETS.md](ASSETS.md)
- [PIPELINE_MAP.md](PIPELINE_MAP.md)
- [PRD Suite Index](prds/README.md)
