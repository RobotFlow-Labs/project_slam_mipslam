"""Numerical integration renderer for projected Gaussians."""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn

from anima_slam_mipslam.gaussians.types import (
    CameraCalibration,
    GaussianMapState,
    GaussianPrimitive,
)
from anima_slam_mipslam.render.autograd import quadratic_form
from anima_slam_mipslam.render.eaa_sampling import EllipticalSamples, sample_elliptical_domain


@dataclass
class RenderCamera:
    intrinsics: torch.Tensor
    height: int
    width: int
    pose_cw: torch.Tensor | None = None


@dataclass
class ProjectedGaussian:
    mean_2d: torch.Tensor
    covariance_2d: torch.Tensor
    depth: torch.Tensor
    opacity: torch.Tensor
    color: torch.Tensor


def _project_gaussian(
    primitive: GaussianPrimitive,
    camera: RenderCamera,
    *,
    eps: float = 1e-6,
) -> ProjectedGaussian | None:
    pose = (
        camera.pose_cw if camera.pose_cw is not None else torch.eye(4, dtype=primitive.mean.dtype)
    )
    mean_h = torch.cat(
        [primitive.mean, torch.ones(1, dtype=primitive.mean.dtype, device=primitive.mean.device)]
    )
    mean_cam = pose @ mean_h
    z = mean_cam[2]
    if z <= eps:
        return None

    x = mean_cam[0] / z
    y = mean_cam[1] / z
    fx = camera.intrinsics[0, 0]
    fy = camera.intrinsics[1, 1]
    cx = camera.intrinsics[0, 2]
    cy = camera.intrinsics[1, 2]
    mean_2d = torch.stack([fx * x + cx, fy * y + cy])

    jacobian = torch.tensor(
        [
            [fx / z, 0.0, -fx * mean_cam[0] / (z * z)],
            [0.0, fy / z, -fy * mean_cam[1] / (z * z)],
        ],
        dtype=primitive.mean.dtype,
        device=primitive.mean.device,
    )
    covariance_2d = (
        jacobian @ primitive.covariance @ jacobian.T
        + torch.eye(2, device=primitive.mean.device) * 1e-4
    )

    color = primitive.color
    if color is None:
        color = primitive.sh_coeffs.mean(dim=0)
    return ProjectedGaussian(
        mean_2d=mean_2d,
        covariance_2d=covariance_2d,
        depth=z.unsqueeze(0),
        opacity=primitive.opacity.reshape(()),
        color=torch.clamp(color.reshape(-1)[:3], 0.0, 1.0),
    )


def project_gaussians(map_state: GaussianMapState, camera: RenderCamera) -> list[ProjectedGaussian]:
    projected: list[ProjectedGaussian] = []
    for primitive in map_state.gaussians:
        projected_gaussian = _project_gaussian(primitive, camera)
        if projected_gaussian is not None:
            projected.append(projected_gaussian)
    return projected


def integrated_opacity(
    sample_bundle: EllipticalSamples, opacity: torch.Tensor, *, eps: float = 1e-6
) -> torch.Tensor:
    qf = quadratic_form(sample_bundle.principal_coords, sample_bundle.eigvals, eps=eps)
    weighted = sample_bundle.weights * torch.exp(-0.5 * qf)
    alpha = opacity * weighted.sum() / torch.clamp(sample_bundle.weights.sum(), min=eps)
    return torch.clamp(alpha, 0.0, 1.0)


def render_projected_gaussians(
    projected_gaussians: list[ProjectedGaussian],
    camera: RenderCamera,
    *,
    base_nodes: int = 3,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    rgb = torch.zeros((camera.height, camera.width, 3), dtype=torch.float32)
    depth = torch.zeros((camera.height, camera.width), dtype=torch.float32)
    alpha_image = torch.zeros((camera.height, camera.width), dtype=torch.float32)

    for gaussian in sorted(projected_gaussians, key=lambda item: float(item.depth)):
        sigma = gaussian.covariance_2d
        radius = int(torch.ceil(2.5 * torch.sqrt(torch.max(torch.linalg.eigvalsh(sigma)))).item())
        cx, cy = gaussian.mean_2d
        x0 = max(0, int(torch.floor(cx).item()) - radius)
        x1 = min(camera.width - 1, int(torch.ceil(cx).item()) + radius)
        y0 = max(0, int(torch.floor(cy).item()) - radius)
        y1 = min(camera.height - 1, int(torch.ceil(cy).item()) + radius)

        for py in range(y0, y1 + 1):
            for px in range(x0, x1 + 1):
                pixel_box = torch.tensor(
                    [px - 0.5, px + 0.5, py - 0.5, py + 0.5],
                    dtype=gaussian.mean_2d.dtype,
                    device=gaussian.mean_2d.device,
                )
                samples = sample_elliptical_domain(
                    gaussian.mean_2d,
                    gaussian.covariance_2d,
                    pixel_box,
                    base_nodes=base_nodes,
                )
                alpha = integrated_opacity(samples, gaussian.opacity)
                transmittance = 1.0 - alpha_image[py, px]
                rgb[py, px] = rgb[py, px] + transmittance * alpha * gaussian.color.to(
                    dtype=rgb.dtype
                )
                depth[py, px] = depth[py, px] + transmittance * alpha * gaussian.depth.to(
                    dtype=depth.dtype
                )
                alpha_image[py, px] = torch.clamp(
                    alpha_image[py, px] + transmittance * alpha, 0.0, 1.0
                )

    return rgb, depth, alpha_image


class EAARenderer(nn.Module):
    """Alias-free renderer operating on Gaussian map state."""

    def __init__(self, *, base_nodes: int = 3) -> None:
        super().__init__()
        self.base_nodes = base_nodes

    def forward(
        self,
        map_state: GaussianMapState,
        calibration: CameraCalibration,
        pose_cw: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        camera = RenderCamera(
            intrinsics=calibration.intrinsics,
            height=calibration.height,
            width=calibration.width,
            pose_cw=pose_cw,
        )
        projected = project_gaussians(map_state, camera)
        return render_projected_gaussians(projected, camera, base_nodes=self.base_nodes)
