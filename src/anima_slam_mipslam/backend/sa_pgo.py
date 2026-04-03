"""Spectral-aware pose graph optimization."""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn

from anima_slam_mipslam.backend.frequency import spectral_confidence_matrix, spectral_signatures


def normalized_graph_laplacian(adjacency: torch.Tensor, *, eps: float = 1e-6) -> torch.Tensor:
    degree = adjacency.sum(dim=-1)
    inv_sqrt = torch.diag(1.0 / torch.sqrt(torch.clamp(degree, min=eps)))
    identity = torch.eye(adjacency.shape[0], dtype=adjacency.dtype, device=adjacency.device)
    return identity - inv_sqrt @ adjacency @ inv_sqrt


def spectral_gap(adjacency: torch.Tensor) -> torch.Tensor:
    degree = torch.diag(adjacency.sum(dim=-1))
    laplacian = degree - adjacency
    eigenvalues = torch.linalg.eigvalsh(laplacian)
    if eigenvalues.numel() < 2:
        return torch.tensor(0.0, dtype=adjacency.dtype, device=adjacency.device)
    return eigenvalues[1]


def prune_edges_by_gap(adjacency: torch.Tensor, *, tau_opt: float = 0.5) -> torch.Tensor:
    gap = spectral_gap(adjacency)
    if gap < tau_opt:
        threshold = 0.75
    else:
        threshold = 0.25
    return torch.where(adjacency >= threshold, adjacency, torch.zeros_like(adjacency))


def optimize_pose_graph(
    poses: torch.Tensor,
    adjacency: torch.Tensor,
    *,
    lambda_spectral: float = 0.25,
    tau_opt: float = 0.5,
) -> torch.Tensor:
    """Lightweight spectral regularization over pose translations."""

    pruned = prune_edges_by_gap(adjacency, tau_opt=tau_opt)
    weights = pruned / pruned.sum(dim=-1, keepdim=True).clamp(min=1e-6)
    translations = poses[:, :3, 3]
    smoothed = weights @ translations
    updated = poses.clone()
    updated[:, :3, 3] = (1.0 - lambda_spectral) * translations + lambda_spectral * smoothed
    return updated


@dataclass
class SAPGOResult:
    poses: torch.Tensor
    adjacency: torch.Tensor
    laplacian_gap: torch.Tensor
    signatures: torch.Tensor


class SpectralAwarePGO(nn.Module):
    def __init__(self, *, beta_c: float = 0.5, beta_g: float = 0.5, tau_opt: float = 0.5) -> None:
        super().__init__()
        self.beta_c = beta_c
        self.beta_g = beta_g
        self.tau_opt = tau_opt

    def forward(self, poses: torch.Tensor, descriptors: torch.Tensor | None = None) -> SAPGOResult:
        signatures = spectral_signatures(poses)
        adjacency = spectral_confidence_matrix(
            signatures,
            poses,
            beta_c=self.beta_c,
            beta_g=self.beta_g,
        )
        if descriptors is not None:
            descriptor_similarity = descriptors @ descriptors.T
            adjacency = 0.5 * adjacency + 0.5 * descriptor_similarity
        updated_poses = optimize_pose_graph(poses, adjacency, tau_opt=self.tau_opt)
        return SAPGOResult(
            poses=updated_poses,
            adjacency=adjacency,
            laplacian_gap=spectral_gap(adjacency),
            signatures=signatures,
        )
