import torch

from anima_slam_mipslam.gaussians.types import CameraCalibration, FrameBatch
from anima_slam_mipslam.pipeline.online_slam import OnlineMipSLAM


def _calibration(width: int = 5, height: int = 5) -> CameraCalibration:
    return CameraCalibration(
        intrinsics=torch.tensor(
            [[20.0, 0.0, width / 2.0], [0.0, 20.0, height / 2.0], [0.0, 0.0, 1.0]],
            dtype=torch.float32,
        ),
        width=width,
        height=height,
    )


def _frame(tx: float) -> FrameBatch:
    rgb = torch.zeros((5, 5, 3), dtype=torch.float32)
    rgb[..., 0] = 1.0
    depth = torch.ones((5, 5), dtype=torch.float32)
    pose = torch.eye(4, dtype=torch.float32)
    pose[0, 3] = tx
    return FrameBatch(rgb=rgb, depth=depth, calibration=_calibration(), pose=pose)


def test_online_pipeline_runs_short_sequence() -> None:
    slam = OnlineMipSLAM()
    result = slam.run([_frame(0.0), _frame(0.1), _frame(0.2)])

    assert result.trajectory.shape == (3, 4, 4)
    assert len(result.map_state.gaussians) >= 1
    assert len(result.pose_graph.poses) == 3
    assert len(result.tracking_losses) == 3
    assert torch.allclose(result.trajectory[-1], result.pose_graph.poses[-1])
