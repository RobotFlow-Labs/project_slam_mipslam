# SLAM-MIPSLAM — Asset Manifest

## Paper
- Title: MipSLAM: Alias-Free Gaussian Splatting SLAM
- ArXiv: 2603.06989
- Authors: Yingzhao Li, Yan Li, Shixiong Tian, Yanjie Liu, Lijun Zhao, Gim Hee Lee
- Primary PDF: `papers/2603.06989_MipSLAM_Alias-Free_Gaussian_Splatting_SLAM.pdf`
- Stale local PDF to ignore: `papers/2503.15908_MipSLAM.pdf`

## Status: ALMOST
- Paper verified and read: DONE
- Source metadata corrected from stale scaffold reference: DONE
- Official GitHub repo located: DONE
- Official GitHub repo contains usable code: MISSING
- Datasets downloaded locally: MISSING
- Reproduction hyperparameters fully disclosed in paper: MISSING

## Reference Code
| Source | URL | Local Path | Status | Notes |
|--------|-----|------------|--------|-------|
| Official repo | https://github.com/yzli1998/MipSLAM | `repositories/MipSLAM` | EMPTY | Repository exists but has no commits as of 2026-04-03 |
| Primary implementation source | https://arxiv.org/abs/2603.06989 | `papers/2603.06989_MipSLAM_Alias-Free_Gaussian_Splatting_SLAM.pdf` | DONE | Paper is the source of truth for EAA and SA-PGO |

## Pretrained Weights
| Model | Size | Source | Path on Server | Status |
|-------|------|--------|---------------|--------|
| MipSLAM checkpoint | Not disclosed | Not disclosed in paper | `/Volumes/AIFlowDev/RobotFlowLabs/models/slam/mipslam/` | MISSING |
| MonoGS compatibility baseline | External baseline, optional | https://github.com/muskie82/MonoGS | `/Volumes/AIFlowDev/RobotFlowLabs/models/slam/monogs/` | OPTIONAL |

## Datasets
| Dataset | Size | Split | Source | Path | Status |
|---------|------|-------|--------|------|--------|
| Replica | 8 benchmark sequences used in paper | Eval | https://github.com/facebookresearch/Replica-Dataset | `/Volumes/AIFlowDev/RobotFlowLabs/datasets/replica/` | MISSING |
| TUM RGB-D | 3 benchmark sequences used in paper | Eval | https://cvg.cit.tum.de/data/datasets/rgbd-dataset | `/Volumes/AIFlowDev/RobotFlowLabs/datasets/tum_rgbd/` | MISSING |

## Hyperparameters And Controls
| Param | Value | Paper Section |
|-------|-------|---------------|
| 3D filter update | `nu_hat[k,t+1] = max(nu_hat[k,t], max_n fn / dn)` | Eq. (3), Sec. III-B.1 |
| EAA importance weight | `w_k = q(x_k) / p(x_k) * psi(kappa, x_k)` | Eq. (5), Sec. III-B.2 |
| Boundary enhancement | `psi(kappa, x_k) = (1 + gamma log kappa) * phi_b(x_k)` | Eq. (5), Sec. III-B.2 |
| Integrated opacity | Importance-weighted elliptical quadrature over `K` points | Eq. (6), Sec. III-B.3 |
| SA-PGO descriptor | Concatenated FFT, gradient, texture, color features | Eq. (8), Sec. III-C.1 |
| Pose spectral window | Hanning-window DFT over `N_w` poses | Eq. (9), Sec. III-C.2 |
| Spectral confidence | `S_ij = beta_c * C_ij + beta_g * G_ij` | Eq. (12), Sec. III-C.2 |
| Global loss | `L = lambda_rgb * L_rgb + lambda_depth * L_depth` | Eq. (15), Sec. III-D |
| `K`, `N_w`, `gamma`, `beta`, `beta_c`, `beta_g`, `lambda_*`, `tau_*` | Not numerically disclosed | Sec. III-B / III-C / III-D |

## Expected Metrics (from paper)
| Benchmark | Metric | Paper Value | Our Target |
|-----------|--------|-------------|-----------|
| Replica, 8-sequence average | PSNR | 35.83 | >= 35.0 |
| Replica, 8-sequence average | SSIM | 0.959 | >= 0.950 |
| Replica, 8-sequence average | LPIPS | 0.048 | <= 0.060 |
| TUM RGB-D, 3-sequence average | PSNR | 22.77 | >= 22.0 |
| TUM RGB-D, 3-sequence average | SSIM | 0.810 | >= 0.790 |
| TUM RGB-D, 3-sequence average | LPIPS | 0.220 | <= 0.240 |
| Replica localization, 8-sequence average | ATE RMSE (cm) | 0.28 | <= 0.35 |

## Resolution Protocol (from paper)
| Dataset | Native Resolution | Evaluation Scales |
|---------|-------------------|-------------------|
| Replica | `680 x 1200` | `2x`, `1x`, `1/2`, `1/4`, `1/8` |
| TUM RGB-D | `480 x 640` | `4x`, `2x`, `1x`, `1/2`, `1/4` |

## Hardware
| Resource | Paper / Project Requirement | Status |
|----------|-----------------------------|--------|
| GPU | NVIDIA RTX 4090 used in paper | External target |
| RGB-D camera | Required for paper-faithful online SLAM | Available through ZED 2i pipeline |
| LiDAR | Not part of paper core method | Optional ANIMA adaptation |

## Implementation Gaps To Track
- The official MipSLAM repo is empty, so all method recovery must come from the paper.
- Numerical values for several optimization weights are omitted; the first reproduction pass must document any inferred defaults explicitly.
- The current scaffold package name is `anima_susanoo`, which should be migrated to `anima_slam_mipslam` in PRD-01.
