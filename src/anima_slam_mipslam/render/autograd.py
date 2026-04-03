"""Helpers for EAA numerical integration gradients."""

from __future__ import annotations

import torch


def quadratic_form(
    principal_coords: torch.Tensor, eigvals: torch.Tensor, *, eps: float = 1e-6
) -> torch.Tensor:
    inverse = 1.0 / torch.clamp(eigvals, min=eps)
    return torch.sum(principal_coords * principal_coords * inverse.unsqueeze(0), dim=-1)


def integrated_opacity_grad(
    principal_coords: torch.Tensor,
    eigvals: torch.Tensor,
    weights: torch.Tensor,
    opacity: torch.Tensor,
    *,
    eps: float = 1e-6,
) -> torch.Tensor:
    """Return the per-axis gradient surrogate from Eq. (7)."""

    qf = quadratic_form(principal_coords, eigvals, eps=eps)
    energy = torch.exp(-0.5 * qf)
    normalizer = torch.clamp(weights.sum(), min=eps)
    return opacity * weights.unsqueeze(-1) * energy.unsqueeze(-1) * principal_coords / normalizer
