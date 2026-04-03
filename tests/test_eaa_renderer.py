import torch

from anima_slam_mipslam.gaussians.types import (
    CameraCalibration,
    GaussianMapState,
    GaussianPrimitive,
)
from anima_slam_mipslam.render.eaa_renderer import EAARenderer


def _primitive(mean, color, opacity=0.8):
    return GaussianPrimitive(
        mean=torch.tensor(mean, dtype=torch.float32),
        covariance=torch.eye(3, dtype=torch.float32) * 0.02,
        opacity=torch.tensor([opacity], dtype=torch.float32),
        sh_coeffs=torch.tensor([[color[0], color[1], color[2]]], dtype=torch.float32),
        color=torch.tensor(color, dtype=torch.float32),
    )


def test_integrated_opacity_is_bounded() -> None:
    map_state = GaussianMapState(gaussians=[_primitive([0.0, 0.0, 1.0], [1.0, 0.0, 0.0])])
    calibration = CameraCalibration(
        intrinsics=torch.tensor(
            [[20.0, 0.0, 2.0], [0.0, 20.0, 2.0], [0.0, 0.0, 1.0]], dtype=torch.float32
        ),
        width=5,
        height=5,
    )
    rgb, depth, alpha = EAARenderer()(map_state, calibration)
    assert torch.all(alpha >= 0.0)
    assert torch.all(alpha <= 1.0)
    assert alpha.max() > 0.0
    assert rgb.sum() > 0.0
    assert depth.sum() > 0.0


def test_closer_gaussian_contributes_first_to_depth() -> None:
    near = _primitive([0.0, 0.0, 1.0], [1.0, 0.0, 0.0], opacity=0.9)
    far = _primitive([0.0, 0.0, 2.0], [0.0, 1.0, 0.0], opacity=0.9)
    map_state = GaussianMapState(gaussians=[far, near])
    calibration = CameraCalibration(
        intrinsics=torch.tensor(
            [[20.0, 0.0, 2.0], [0.0, 20.0, 2.0], [0.0, 0.0, 1.0]], dtype=torch.float32
        ),
        width=5,
        height=5,
    )
    _, depth, alpha = EAARenderer()(map_state, calibration)
    center_depth = depth[2, 2] / alpha[2, 2].clamp(min=1e-6)
    assert center_depth < 1.5
