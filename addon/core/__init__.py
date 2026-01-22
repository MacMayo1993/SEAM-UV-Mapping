"""
Core algorithm implementation for non-orientable UV unwrapping.

This module contains the standalone Python implementation that can be used
independently of Blender.
"""

from .topology import TopologicalUVAtlas
from .curvature import compute_gaussian_curvature
from .parity import assign_parity
from .uv_generation import generate_uvs
from .distortion import (
    compute_angle_distortion,
    compute_area_distortion,
    compute_uv_coverage
)

__all__ = [
    "TopologicalUVAtlas",
    "compute_gaussian_curvature",
    "assign_parity",
    "generate_uvs",
    "compute_angle_distortion",
    "compute_area_distortion",
    "compute_uv_coverage",
]
