import torch

from anima_slam_mipslam.backend.descriptors import compute_multi_modal_descriptor
from anima_slam_mipslam.backend.sa_pgo import SpectralAwarePGO, prune_edges_by_gap, spectral_gap


def _pose(tx: float) -> torch.Tensor:
    pose = torch.eye(4, dtype=torch.float32)
    pose[0, 3] = tx
    return pose


def test_descriptor_has_expected_modalities() -> None:
    rgb = torch.ones((8, 8, 3), dtype=torch.float32) * 0.5
    depth = torch.ones((8, 8), dtype=torch.float32)
    descriptor = compute_multi_modal_descriptor(rgb, depth)
    assert descriptor.ndim == 1
    assert descriptor.numel() == 44


def test_laplacian_gap_controls_edge_pruning() -> None:
    disconnected = torch.tensor([[0.0, 0.2], [0.2, 0.0]], dtype=torch.float32)
    connected = torch.tensor([[0.0, 0.9], [0.9, 0.0]], dtype=torch.float32)
    assert spectral_gap(connected) > spectral_gap(disconnected)
    assert prune_edges_by_gap(disconnected, tau_opt=0.5).sum() == 0.0
    assert prune_edges_by_gap(connected, tau_opt=0.5).sum() > 0.0


def test_sa_pgo_returns_pose_updates() -> None:
    poses = torch.stack([_pose(0.0), _pose(2.0), _pose(4.0)], dim=0)
    descriptors = torch.eye(3, dtype=torch.float32)
    result = SpectralAwarePGO()(poses, descriptors)
    assert result.poses.shape == poses.shape
    assert result.adjacency.shape == (3, 3)
    assert result.laplacian_gap >= 0.0
