"""Multi-modal descriptors for SA-PGO."""

from __future__ import annotations

import torch
import torch.nn.functional as F


def _l2_normalize(x: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    return x / torch.clamp(torch.linalg.norm(x), min=eps)


def _grayscale(rgb: torch.Tensor) -> torch.Tensor:
    return (0.2989 * rgb[..., 0] + 0.5870 * rgb[..., 1] + 0.1140 * rgb[..., 2]).to(torch.float32)


def _fft_features(gray: torch.Tensor, bins: int = 8) -> torch.Tensor:
    spectrum = torch.fft.rfft2(gray)
    magnitude = torch.abs(spectrum)
    flat = magnitude.flatten()
    chunks = torch.chunk(flat, bins)
    return torch.stack(
        [
            chunk.mean() if chunk.numel() else torch.tensor(0.0, device=gray.device)
            for chunk in chunks
        ]
    )


def _gradient_features(gray: torch.Tensor) -> torch.Tensor:
    image = gray.unsqueeze(0).unsqueeze(0)
    sobel_x = torch.tensor(
        [[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]], device=gray.device
    )
    sobel_y = sobel_x.T
    kernels = torch.stack([sobel_x, sobel_y]).unsqueeze(1)
    gradients = F.conv2d(image, kernels, padding=1)
    stats = torch.stack(
        [
            gradients[0, 0].mean(),
            gradients[0, 1].mean(),
            gradients[0, 0].std(),
            gradients[0, 1].std(),
            torch.sqrt(gradients.square().sum(dim=1)).mean(),
            torch.sqrt(gradients.square().sum(dim=1)).std(),
        ]
    )
    return stats


def _texture_features(gray: torch.Tensor) -> torch.Tensor:
    image = gray.unsqueeze(0).unsqueeze(0)
    laplacian = torch.tensor(
        [[0.0, 1.0, 0.0], [1.0, -4.0, 1.0], [0.0, 1.0, 0.0]], device=gray.device
    )
    blur = torch.full((3, 3), 1.0 / 9.0, device=gray.device)
    kernels = torch.stack([laplacian, blur]).unsqueeze(1)
    responses = F.conv2d(image, kernels, padding=1)
    return torch.stack(
        [
            responses[0, 0].mean(),
            responses[0, 0].std(),
            responses[0, 1].mean(),
            responses[0, 1].std(),
        ]
    )


def _color_features(rgb: torch.Tensor, bins: int = 8) -> torch.Tensor:
    features = []
    for channel in range(3):
        hist = torch.histc(rgb[..., channel], bins=bins, min=0.0, max=1.0)
        features.append(hist)
    return torch.cat(features)


def compute_multi_modal_descriptor(
    rgb: torch.Tensor, depth: torch.Tensor | None = None
) -> torch.Tensor:
    """Compute the descriptor in Eq. (8) with per-modality normalization."""

    rgb = rgb.to(torch.float32)
    gray = _grayscale(rgb)
    fft_features = _l2_normalize(_fft_features(gray))
    gradient_features = _l2_normalize(_gradient_features(gray))
    texture_features = _l2_normalize(_texture_features(gray))
    color_features = _l2_normalize(_color_features(rgb))
    if depth is not None:
        depth_stats = _l2_normalize(torch.stack([depth.mean(), depth.std()]))
        return torch.cat(
            [fft_features, gradient_features, texture_features, color_features, depth_stats]
        )
    return torch.cat([fft_features, gradient_features, texture_features, color_features])
