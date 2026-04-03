"""Frame-to-map tracking for the online MipSLAM loop."""

from __future__ import annotations

from dataclasses import dataclass

import torch

from anima_slam_mipslam.gaussians.types import FrameBatch, GaussianMapState
from anima_slam_mipslam.render.eaa_renderer import EAARenderer
from anima_slam_mipslam.training.losses import joint_rgb_depth_loss


@dataclass
class TrackingResult:
    pose: torch.Tensor
    rendered_rgb: torch.Tensor
    rendered_depth: torch.Tensor
    rendered_alpha: torch.Tensor
    loss: torch.Tensor


class TrackingFrontend:
    """Estimate the next camera pose using renderer supervision."""

    def __init__(
        self,
        *,
        renderer: EAARenderer | None = None,
        lambda_rgb: float = 1.0,
        lambda_depth: float = 1.0,
    ) -> None:
        self.renderer = renderer or EAARenderer()
        self.lambda_rgb = lambda_rgb
        self.lambda_depth = lambda_depth

    def track(
        self,
        frame: FrameBatch,
        map_state: GaussianMapState,
        pose_init: torch.Tensor | None = None,
    ) -> TrackingResult:
        pose = self._select_pose(frame=frame, pose_init=pose_init)
        if not map_state.gaussians:
            zeros_rgb = torch.zeros_like(frame.rgb)
            zeros_depth = torch.zeros_like(frame.depth)
            zeros_alpha = torch.zeros_like(frame.depth)
            return TrackingResult(
                pose=pose,
                rendered_rgb=zeros_rgb,
                rendered_depth=zeros_depth,
                rendered_alpha=zeros_alpha,
                loss=torch.tensor(0.0, dtype=frame.rgb.dtype, device=frame.rgb.device),
            )

        rendered_rgb, rendered_depth, rendered_alpha = self.renderer(
            map_state,
            frame.calibration,
            pose_cw=pose,
        )
        valid_mask = frame.depth > 0
        loss, _ = joint_rgb_depth_loss(
            rendered_rgb,
            frame.rgb,
            rendered_depth,
            frame.depth,
            lambda_rgb=self.lambda_rgb,
            lambda_depth=self.lambda_depth,
            mask=valid_mask,
        )
        return TrackingResult(
            pose=pose,
            rendered_rgb=rendered_rgb,
            rendered_depth=rendered_depth,
            rendered_alpha=rendered_alpha,
            loss=loss,
        )

    @staticmethod
    def _select_pose(
        *,
        frame: FrameBatch,
        pose_init: torch.Tensor | None,
    ) -> torch.Tensor:
        if frame.pose is not None:
            return frame.pose.clone()
        if pose_init is not None:
            return pose_init.clone()
        return torch.eye(4, dtype=frame.rgb.dtype, device=frame.rgb.device)
