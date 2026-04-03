"""Frequency-domain trajectory analysis for SA-PGO."""

from __future__ import annotations

import torch


def pose_matrices_to_vectors(poses: torch.Tensor) -> torch.Tensor:
    translations = poses[:, :3, 3]
    rotations = poses[:, :3, :3]
    trace = torch.clamp(rotations.diagonal(dim1=-2, dim2=-1).sum(-1), min=-1.0, max=3.0)
    angles = torch.arccos(torch.clamp((trace - 1.0) * 0.5, min=-1.0, max=1.0))
    axis = torch.stack(
        [
            rotations[:, 2, 1] - rotations[:, 1, 2],
            rotations[:, 0, 2] - rotations[:, 2, 0],
            rotations[:, 1, 0] - rotations[:, 0, 1],
        ],
        dim=-1,
    )
    axis_norm = torch.linalg.norm(axis, dim=-1, keepdim=True).clamp(min=1e-6)
    axis_angle = axis / axis_norm * angles.unsqueeze(-1)
    return torch.cat([translations, axis_angle], dim=-1)


def spectral_signatures(poses: torch.Tensor, *, window_size: int | None = None) -> torch.Tensor:
    vectors = pose_matrices_to_vectors(poses)
    num_poses = vectors.shape[0]
    window_size = num_poses if window_size is None else min(window_size, num_poses)
    half_window = max(1, window_size // 2)
    signatures = []
    for center in range(num_poses):
        start = max(0, center - half_window)
        end = min(num_poses, start + window_size)
        window = vectors[start:end]
        if window.shape[0] == 1:
            window = window.repeat(2, 1)
        hann = torch.hann_window(
            window.shape[0], periodic=False, dtype=window.dtype, device=window.device
        )
        weighted = window * hann.unsqueeze(-1)
        spectrum = torch.fft.rfft(weighted, dim=0)
        power = torch.abs(spectrum) ** 2
        freqs = torch.arange(power.shape[0], dtype=window.dtype, device=window.device).unsqueeze(-1)
        centroid = (freqs * power).sum(dim=0) / power.sum(dim=0).clamp(min=1e-6)
        signatures.append(centroid)
    return torch.stack(signatures, dim=0)


def frequency_coherence_matrix(signatures: torch.Tensor) -> torch.Tensor:
    normalized = signatures / torch.linalg.norm(signatures, dim=-1, keepdim=True).clamp(min=1e-6)
    cosine = normalized @ normalized.T
    return 0.5 * (1.0 + cosine)


def geometric_regularities(
    poses: torch.Tensor, *, alpha_t: float = 1.0, alpha_r: float = 0.5
) -> torch.Tensor:
    vectors = pose_matrices_to_vectors(poses)
    translations = vectors[:, :3]
    rotations = vectors[:, 3:]
    t_dist = torch.cdist(translations, translations)
    r_dist = torch.cdist(rotations, rotations)
    return torch.exp(-alpha_t * t_dist - alpha_r * r_dist)


def spectral_confidence_matrix(
    signatures: torch.Tensor,
    poses: torch.Tensor,
    *,
    beta_c: float = 0.5,
    beta_g: float = 0.5,
) -> torch.Tensor:
    coherence = frequency_coherence_matrix(signatures)
    regularity = geometric_regularities(poses)
    return beta_c * coherence + beta_g * regularity
