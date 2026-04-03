"""Frequency-aware backend modules."""

from .descriptors import compute_multi_modal_descriptor
from .frequency import (
    frequency_coherence_matrix,
    geometric_regularities,
    spectral_confidence_matrix,
    spectral_signatures,
)
from .sa_pgo import SpectralAwarePGO, normalized_graph_laplacian, optimize_pose_graph, spectral_gap

__all__ = [
    "SpectralAwarePGO",
    "compute_multi_modal_descriptor",
    "frequency_coherence_matrix",
    "geometric_regularities",
    "normalized_graph_laplacian",
    "optimize_pose_graph",
    "spectral_confidence_matrix",
    "spectral_gap",
    "spectral_signatures",
]
