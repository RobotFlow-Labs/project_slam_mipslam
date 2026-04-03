import torch

from anima_slam_mipslam.gaussians.types import GaussianPrimitive


def test_gaussian_covariance_is_3x3() -> None:
    primitive = GaussianPrimitive(
        mean=torch.zeros(3),
        covariance=torch.eye(3),
        opacity=torch.ones(1),
        sh_coeffs=torch.zeros(1, 3),
    )
    assert primitive.covariance.shape == (3, 3)
    assert primitive.mean.shape == (3,)
