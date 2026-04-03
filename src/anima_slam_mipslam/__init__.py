"""ANIMA SLAM-MIPSLAM foundation package."""

from .device import get_backend, get_device
from .version import __version__

__all__ = ["__version__", "get_backend", "get_device"]
