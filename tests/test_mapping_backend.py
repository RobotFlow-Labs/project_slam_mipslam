import torch

from anima_slam_mipslam.gaussians.types import CameraCalibration, FrameBatch, GaussianMapState
from anima_slam_mipslam.mapping.backend import MappingBackend


def _calibration() -> CameraCalibration:
    return CameraCalibration(
        intrinsics=torch.tensor(
            [[20.0, 0.0, 2.0], [0.0, 20.0, 2.0], [0.0, 0.0, 1.0]],
            dtype=torch.float32,
        ),
        width=5,
        height=5,
    )


def _frame(tx: float) -> FrameBatch:
    rgb = torch.zeros((5, 5, 3), dtype=torch.float32)
    rgb[..., 0] = 1.0
    depth = torch.ones((5, 5), dtype=torch.float32)
    pose = torch.eye(4, dtype=torch.float32)
    pose[0, 3] = tx
    return FrameBatch(rgb=rgb, depth=depth, calibration=_calibration(), pose=pose)


def test_keyframe_window_updates() -> None:
    backend = MappingBackend(active_window_size=2, keyframe_interval=1, sa_pgo_interval=2)
    map_state = GaussianMapState(gaussians=[])

    for offset in [0.0, 0.1, 0.2]:
        backend.update(_frame(offset), _frame(offset).pose, map_state)

    assert len(backend.keyframes) == 3
    assert map_state.active_keyframe_ids == [1, 2]
    assert len(map_state.gaussians) == 3
    assert map_state.global_scale_support is not None
    adjacency = backend.covisibility_adjacency()
    assert adjacency.shape == (3, 3)
    assert adjacency.sum() > 0
