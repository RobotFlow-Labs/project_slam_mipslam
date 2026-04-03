import torch

from anima_slam_mipslam.training.losses import joint_rgb_depth_loss


def test_joint_loss_is_zero_for_identical_inputs() -> None:
    rgb = torch.zeros((2, 2, 3), dtype=torch.float32)
    depth = torch.zeros((2, 2), dtype=torch.float32)
    total, parts = joint_rgb_depth_loss(rgb, rgb, depth, depth)
    assert torch.isclose(total, torch.tensor(0.0))
    assert torch.isclose(parts["rgb"], torch.tensor(0.0))
    assert torch.isclose(parts["depth"], torch.tensor(0.0))


def test_joint_loss_combines_rgb_and_depth_terms() -> None:
    rgb_pred = torch.ones((1, 1, 3), dtype=torch.float32)
    rgb_gt = torch.zeros((1, 1, 3), dtype=torch.float32)
    depth_pred = torch.ones((1, 1), dtype=torch.float32)
    depth_gt = torch.zeros((1, 1), dtype=torch.float32)
    total, parts = joint_rgb_depth_loss(
        rgb_pred, rgb_gt, depth_pred, depth_gt, lambda_rgb=2.0, lambda_depth=3.0
    )
    assert torch.isclose(total, 2.0 * parts["rgb"] + 3.0 * parts["depth"])
