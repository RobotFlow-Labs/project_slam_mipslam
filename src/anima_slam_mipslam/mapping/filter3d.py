"""Incremental 3D filtering from MipSLAM Eq. (3)."""

from __future__ import annotations

import torch


def update_sampling_frequency(
    nu_hat: torch.Tensor,
    focal_length: torch.Tensor | float,
    depths: torch.Tensor,
    *,
    eps: float = 1e-6,
) -> torch.Tensor:
    """Apply Eq. (3) with a vector of observed depths."""

    focal = torch.as_tensor(focal_length, dtype=depths.dtype, device=depths.device)
    safe_depths = torch.clamp(depths, min=eps)
    candidate = focal / safe_depths
    if candidate.ndim > 1:
        candidate = candidate.max(dim=-1).values
    return torch.maximum(nu_hat, candidate)


def update_sampling_frequency_from_keyframes(
    nu_hat: torch.Tensor,
    focal_lengths: torch.Tensor,
    observed_depths: torch.Tensor,
    visibility_mask: torch.Tensor,
    *,
    eps: float = 1e-6,
) -> torch.Tensor:
    """Update per-Gaussian frequency support across active keyframes.

    Shapes:
    - ``nu_hat``: ``[num_gaussians]``
    - ``focal_lengths``: ``[num_keyframes]``
    - ``observed_depths``: ``[num_gaussians, num_keyframes]``
    - ``visibility_mask``: ``[num_gaussians, num_keyframes]`` bool
    """

    focal = focal_lengths.unsqueeze(0).to(
        dtype=observed_depths.dtype, device=observed_depths.device
    )
    safe_depths = torch.clamp(observed_depths, min=eps)
    candidate = focal / safe_depths
    masked = torch.where(visibility_mask, candidate, torch.zeros_like(candidate))
    return torch.maximum(nu_hat, masked.max(dim=-1).values)
