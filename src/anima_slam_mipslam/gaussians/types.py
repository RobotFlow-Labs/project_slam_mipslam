"""Typed data contracts used by the MipSLAM implementation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import torch


@dataclass(frozen=True)
class ResolutionScale:
    name: str
    factor: float


@dataclass
class CameraCalibration:
    intrinsics: torch.Tensor
    width: int
    height: int
    depth_scale: float = 1000.0
    frame_id: str = "camera"


@dataclass
class FrameBatch:
    rgb: torch.Tensor
    depth: torch.Tensor
    calibration: CameraCalibration
    pose: torch.Tensor | None = None
    timestamp: float | None = None
    source_path: Path | None = None
    sequence_name: str = ""
    scale: ResolutionScale = field(default_factory=lambda: ResolutionScale(name="1x", factor=1.0))


@dataclass
class GaussianPrimitive:
    mean: torch.Tensor
    covariance: torch.Tensor
    opacity: torch.Tensor
    sh_coeffs: torch.Tensor
    color: torch.Tensor | None = None


@dataclass
class GaussianMapState:
    gaussians: list[GaussianPrimitive]
    active_keyframe_ids: list[int] = field(default_factory=list)
    global_scale_support: torch.Tensor | None = None


@dataclass
class KeyframeRecord:
    keyframe_id: int
    frame: FrameBatch
    visibility_ids: list[int] = field(default_factory=list)


@dataclass
class PoseGraphEdge:
    source_id: int
    target_id: int
    transform: torch.Tensor
    information: torch.Tensor
    spectral_confidence: float = 0.0


@dataclass
class PoseGraphState:
    poses: list[torch.Tensor]
    edges: list[PoseGraphEdge]
    laplacian_gap: float | None = None

