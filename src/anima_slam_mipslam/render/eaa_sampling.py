"""Elliptical Adaptive Anti-aliasing sampling from MipSLAM Eq. (5)."""

from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass
class EllipticalSamples:
    sample_points: torch.Tensor
    principal_coords: torch.Tensor
    weights: torch.Tensor
    eigvals: torch.Tensor
    eigvecs: torch.Tensor
    condition_number: torch.Tensor
    boundary_distance: torch.Tensor
    pixel_box: torch.Tensor


def _distance_to_box(point: torch.Tensor, pixel_box: torch.Tensor) -> torch.Tensor:
    x_min, x_max, y_min, y_max = pixel_box.unbind()
    dx = torch.minimum(point[..., 0] - x_min, x_max - point[..., 0])
    dy = torch.minimum(point[..., 1] - y_min, y_max - point[..., 1])
    return torch.minimum(dx, dy)


def sample_elliptical_domain(
    mu_2d: torch.Tensor,
    sigma_2d: torch.Tensor,
    pixel_box: torch.Tensor,
    *,
    base_nodes: int = 3,
    gamma: float = 0.5,
    beta: float = 2.0,
    eps: float = 1e-6,
) -> EllipticalSamples:
    """Sample a projected Gaussian in its principal-axis frame.

    The proposal density is a deterministic grid in principal-axis space.
    ``weights`` stores the unnormalized importance terms from Eq. (5).
    """

    eigvals, eigvecs = torch.linalg.eigh(sigma_2d)
    eigvals = torch.clamp(eigvals, min=eps)
    order = torch.argsort(eigvals, descending=True)
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]
    condition_number = eigvals[0] / eigvals[-1]

    extra_nodes = int(torch.ceil(torch.log(condition_number + 1.0)).item())
    num_nodes = max(base_nodes, base_nodes + extra_nodes)
    nodes = torch.linspace(-1.0, 1.0, num_nodes, dtype=mu_2d.dtype, device=mu_2d.device)
    principal_coords = torch.cartesian_prod(nodes, nodes) * torch.sqrt(eigvals).unsqueeze(0)
    sample_points = principal_coords @ eigvecs.T + mu_2d.unsqueeze(0)

    inverse_scale = torch.rsqrt(eigvals).unsqueeze(0)
    gaussian_energy = torch.sum((principal_coords * inverse_scale) ** 2, dim=-1)
    target_density = torch.exp(-0.5 * gaussian_energy)

    proposal_density = torch.full_like(target_density, 1.0 / target_density.numel())
    boundary_distance = torch.clamp(_distance_to_box(sample_points, pixel_box), min=0.0)
    boundary_term = torch.exp(-beta * boundary_distance)
    geometry_term = (1.0 + gamma * torch.log(condition_number)) * boundary_term
    weights = target_density / proposal_density * geometry_term

    return EllipticalSamples(
        sample_points=sample_points,
        principal_coords=principal_coords,
        weights=weights,
        eigvals=eigvals,
        eigvecs=eigvecs,
        condition_number=condition_number,
        boundary_distance=boundary_distance,
        pixel_box=pixel_box,
    )
