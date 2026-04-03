import torch

from anima_slam_mipslam.gaussians.types import CameraCalibration, FrameBatch
from anima_slam_mipslam.pipeline.online_slam import OnlineMipSLAM


def _frame() -> FrameBatch:
    rgb = torch.zeros((5, 5, 3), dtype=torch.float32)
    rgb[..., 0] = 1.0
    depth = torch.ones((5, 5), dtype=torch.float32)
    pose = torch.eye(4, dtype=torch.float32)
    return FrameBatch(
        rgb=rgb,
        depth=depth,
        calibration=CameraCalibration(
            intrinsics=torch.tensor(
                [[20.0, 0.0, 2.0], [0.0, 20.0, 2.0], [0.0, 0.0, 1.0]],
                dtype=torch.float32,
            ),
            width=5,
            height=5,
        ),
        pose=pose,
    )


def test_saved_map_rerenders_under_new_intrinsics() -> None:
    slam = OnlineMipSLAM()
    slam.run([_frame(), _frame()])

    native = CameraCalibration(
        intrinsics=torch.tensor(
            [[20.0, 0.0, 2.0], [0.0, 20.0, 2.0], [0.0, 0.0, 1.0]],
            dtype=torch.float32,
        ),
        width=5,
        height=5,
    )
    scaled = CameraCalibration(
        intrinsics=torch.tensor(
            [[40.0, 0.0, 4.0], [0.0, 40.0, 4.0], [0.0, 0.0, 1.0]],
            dtype=torch.float32,
        ),
        width=9,
        height=9,
    )

    rgb_native, _, alpha_native = slam.render_map(native)
    rgb_scaled, _, alpha_scaled = slam.render_map(scaled)

    assert rgb_native.shape == (5, 5, 3)
    assert rgb_scaled.shape == (9, 9, 3)
    assert alpha_native.sum() > 0
    assert alpha_scaled.sum() > 0
    assert torch.isclose(rgb_native.mean(), rgb_scaled.mean(), atol=0.25)
