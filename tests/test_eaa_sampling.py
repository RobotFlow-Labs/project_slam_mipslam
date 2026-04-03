import torch

from anima_slam_mipslam.render.eaa_sampling import sample_elliptical_domain


def test_sampling_weights_favor_high_condition_number() -> None:
    mu = torch.tensor([0.0, 0.0])
    pixel_box = torch.tensor([-0.5, 0.5, -0.5, 0.5])
    isotropic = sample_elliptical_domain(mu, torch.diag(torch.tensor([1.0, 1.0])), pixel_box)
    anisotropic = sample_elliptical_domain(mu, torch.diag(torch.tensor([9.0, 1.0])), pixel_box)
    assert anisotropic.condition_number > isotropic.condition_number
    assert anisotropic.weights.numel() > isotropic.weights.numel()
