import torch

from anima_slam_mipslam.gaussians.types import (
    CameraCalibration,
    FrameBatch,
    GaussianMapState,
    GaussianPrimitive,
)
from anima_slam_mipslam.tracking.frontend import TrackingFrontend


def _calibration(size: int = 5) -> CameraCalibration:
    return CameraCalibration(
        intrinsics=torch.tensor(
            [[20.0, 0.0, 2.0], [0.0, 20.0, 2.0], [0.0, 0.0, 1.0]],
            dtype=torch.float32,
        ),
        width=size,
        height=size,
    )


def _frame(color: float = 1.0) -> FrameBatch:
    rgb = torch.zeros((5, 5, 3), dtype=torch.float32)
    rgb[..., 0] = color
    depth = torch.ones((5, 5), dtype=torch.float32)
    return FrameBatch(
        rgb=rgb,
        depth=depth,
        calibration=_calibration(),
        pose=torch.eye(4, dtype=torch.float32),
    )


def _map_state() -> GaussianMapState:
    primitive = GaussianPrimitive(
        mean=torch.tensor([0.0, 0.0, 1.0], dtype=torch.float32),
        covariance=torch.eye(3, dtype=torch.float32) * 0.01,
        opacity=torch.tensor([0.9], dtype=torch.float32),
        sh_coeffs=torch.tensor([[1.0, 0.0, 0.0]], dtype=torch.float32),
        color=torch.tensor([1.0, 0.0, 0.0], dtype=torch.float32),
    )
    return GaussianMapState(gaussians=[primitive])


def test_tracking_step_returns_pose_matrix() -> None:
    frontend = TrackingFrontend()
    result = frontend.track(_frame(), _map_state())
    assert result.pose.shape == (4, 4)
    assert result.rendered_rgb.shape == (5, 5, 3)
    assert result.rendered_depth.shape == (5, 5)
    assert torch.isfinite(result.loss)
