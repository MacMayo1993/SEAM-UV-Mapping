"""
Pytest configuration and fixtures for test suite.
"""

from pathlib import Path

import numpy as np
import pytest

# Test fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"
FIXTURES_DIR.mkdir(exist_ok=True)


@pytest.fixture
def sphere_mesh_simple():
    """Simple sphere mesh for testing (8 vertices, icosahedron subdivision)"""
    # Create simple icosahedron
    phi = (1 + np.sqrt(5)) / 2

    vertices = np.array([
        [-1, phi, 0], [1, phi, 0], [-1, -phi, 0], [1, -phi, 0],
        [0, -1, phi], [0, 1, phi], [0, -1, -phi], [0, 1, -phi],
        [phi, 0, -1], [phi, 0, 1], [-phi, 0, -1], [-phi, 0, 1]
    ], dtype=np.float64)

    # Normalize to unit sphere
    vertices /= np.linalg.norm(vertices, axis=1, keepdims=True)

    triangles = np.array([
        [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
        [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
        [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
        [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]
    ], dtype=np.int32)

    return vertices, triangles


@pytest.fixture
def plane_mesh():
    """Simple plane mesh for testing (flat, should have zero curvature)"""
    vertices = np.array([
        [0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0],
        [0, 2, 0], [1, 2, 0]
    ], dtype=np.float64)

    triangles = np.array([
        [0, 1, 2], [1, 3, 2],
        [2, 3, 4], [3, 5, 4]
    ], dtype=np.int32)

    return vertices, triangles


@pytest.fixture
def cylinder_mesh():
    """Simple cylinder mesh for testing"""
    n_segments = 8
    angles = np.linspace(0, 2 * np.pi, n_segments, endpoint=False)

    # Create two rings
    vertices = []
    for z in [0, 1]:
        for angle in angles:
            x = np.cos(angle)
            y = np.sin(angle)
            vertices.append([x, y, z])

    vertices = np.array(vertices, dtype=np.float64)

    # Create triangles
    triangles = []
    for i in range(n_segments):
        next_i = (i + 1) % n_segments

        # Bottom triangle
        v0 = i
        v1 = next_i
        v2 = i + n_segments
        v3 = next_i + n_segments

        triangles.append([v0, v1, v2])
        triangles.append([v1, v3, v2])

    triangles = np.array(triangles, dtype=np.int32)

    return vertices, triangles


@pytest.fixture
def non_manifold_mesh():
    """Non-manifold mesh for testing error handling"""
    # Create mesh with shared edge between 3 faces (non-manifold)
    vertices = np.array([
        [0, 0, 0], [1, 0, 0], [0.5, 1, 0],
        [0.5, -1, 0]
    ], dtype=np.float64)

    # Three triangles sharing edge (0, 1)
    triangles = np.array([
        [0, 1, 2],
        [0, 1, 3],
        [1, 0, 2]  # Duplicate with different winding
    ], dtype=np.int32)

    return vertices, triangles
