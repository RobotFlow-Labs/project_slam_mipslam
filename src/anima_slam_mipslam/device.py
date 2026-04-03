"""Device and backend selection for macOS prebuild and later CUDA training."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class BackendInfo:
    name: str
    torch_device: str


def _detect_backend() -> BackendInfo:
    requested = os.environ.get("ANIMA_BACKEND", "auto").lower()
    if requested == "mlx":
        return BackendInfo(name="mlx", torch_device="cpu")
    if requested == "cuda":
        return BackendInfo(name="cuda", torch_device="cuda")
    if requested == "cpu":
        return BackendInfo(name="cpu", torch_device="cpu")

    try:
        import mlx.core as mx  # noqa: F401

        return BackendInfo(name="mlx", torch_device="cpu")
    except ImportError:
        pass

    try:
        import torch

        if torch.cuda.is_available():
            return BackendInfo(name="cuda", torch_device="cuda")
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return BackendInfo(name="mps", torch_device="mps")
        return BackendInfo(name="cpu", torch_device="cpu")
    except ImportError:
        return BackendInfo(name="cpu", torch_device="cpu")


_BACKEND = _detect_backend()


def get_backend() -> str:
    return _BACKEND.name


def get_device():
    import torch

    return torch.device(_BACKEND.torch_device)

