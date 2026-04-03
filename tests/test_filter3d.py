import torch

from anima_slam_mipslam.mapping.filter3d import (
    update_sampling_frequency,
    update_sampling_frequency_from_keyframes,
)


def test_sampling_frequency_is_monotonic() -> None:
    nu_hat = torch.tensor([1.0, 2.0])
    depths = torch.tensor([5.0, 4.0])
    updated = update_sampling_frequency(nu_hat, focal_length=20.0, depths=depths)
    assert torch.all(updated >= nu_hat)


def test_sampling_frequency_respects_visibility_mask() -> None:
    nu_hat = torch.tensor([0.1, 0.1])
    focal_lengths = torch.tensor([10.0, 20.0])
    depths = torch.tensor([[10.0, 2.0], [5.0, 5.0]])
    visibility = torch.tensor([[True, False], [True, True]])
    updated = update_sampling_frequency_from_keyframes(nu_hat, focal_lengths, depths, visibility)
    assert torch.allclose(updated, torch.tensor([1.0, 4.0]))
