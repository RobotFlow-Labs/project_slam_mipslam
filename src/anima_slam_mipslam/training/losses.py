"""Loss functions from MipSLAM Eq. (15)."""

from __future__ import annotations

import torch


def joint_rgb_depth_loss(
    rgb_pred: torch.Tensor,
    rgb_gt: torch.Tensor,
    depth_pred: torch.Tensor,
    depth_gt: torch.Tensor,
    *,
    lambda_rgb: float = 1.0,
    lambda_depth: float = 1.0,
    mask: torch.Tensor | None = None,
) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
    if mask is not None:
        rgb_pred = rgb_pred[mask]
        rgb_gt = rgb_gt[mask]
        depth_pred = depth_pred[mask]
        depth_gt = depth_gt[mask]
    rgb_loss = torch.mean((rgb_pred - rgb_gt) ** 2)
    depth_loss = torch.mean((depth_pred - depth_gt) ** 2)
    total = lambda_rgb * rgb_loss + lambda_depth * depth_loss
    return total, {"rgb": rgb_loss, "depth": depth_loss}
