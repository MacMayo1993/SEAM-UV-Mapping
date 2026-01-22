"""
UV coordinate generation with parity-aware antipodal correction.

Generates UV coordinates using spherical parameterization, then applies
antipodal correction for negative-parity vertices.
"""

import numpy as np
from scipy.optimize import minimize
from typing import Optional


def generate_uvs(
    vertices: np.ndarray,
    triangles: np.ndarray,
    parities: np.ndarray,
    method: str = "spherical"
) -> np.ndarray:
    """
    Generate UV coordinates with parity-aware correction.

    Args:
        vertices: (N, 3) array of vertex positions
        triangles: (M, 3) array of triangle indices
        parities: (N,) array of vertex parities ±1
        method: Parameterization method ("spherical", "lscm", "conformal")

    Returns:
        (N, 2) array of UV coordinates in [0, 1]²
    """
    if method == "spherical":
        uvs = _spherical_parameterization(vertices)
    elif method == "lscm":
        uvs = _lscm_parameterization(vertices, triangles)
    else:
        raise ValueError(f"Unknown parameterization method: {method}")

    # Apply antipodal correction for negative parity
    uvs_corrected = uvs.copy()
    negative_mask = parities < 0
    uvs_corrected[negative_mask] = 1.0 - uvs[negative_mask]

    return uvs_corrected


def _spherical_parameterization(vertices: np.ndarray) -> np.ndarray:
    """
    Spherical parameterization: project vertices to unit sphere and compute UV.

    UV coordinates are computed as:
        u = (1 + atan2(y, x) / π) / 2
        v = acos(z) / π

    Args:
        vertices: (N, 3) array of vertex positions

    Returns:
        (N, 2) array of UV coordinates in [0, 1]²
    """
    # Normalize to unit sphere
    norms = np.linalg.norm(vertices, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-10)  # Avoid division by zero
    vertices_normalized = vertices / norms

    x = vertices_normalized[:, 0]
    y = vertices_normalized[:, 1]
    z = vertices_normalized[:, 2]

    # Spherical coordinates
    u = (1.0 + np.arctan2(y, x) / np.pi) / 2.0
    v = np.arccos(np.clip(z, -1.0, 1.0)) / np.pi

    uvs = np.stack([u, v], axis=1)
    return uvs


def _lscm_parameterization(
    vertices: np.ndarray,
    triangles: np.ndarray
) -> np.ndarray:
    """
    Least Squares Conformal Maps (LSCM) parameterization.

    This is a simplified implementation. For production use, consider
    using optimized libraries like libigl.

    Args:
        vertices: (N, 3) array of vertex positions
        triangles: (M, 3) array of triangle indices

    Returns:
        (N, 2) array of UV coordinates
    """
    # For now, fall back to spherical
    # Full LSCM implementation requires sparse linear solver
    return _spherical_parameterization(vertices)


def optimize_uvs_for_distortion(
    vertices: np.ndarray,
    triangles: np.ndarray,
    uvs_init: np.ndarray,
    max_iter: int = 100
) -> np.ndarray:
    """
    Optimize UV coordinates to minimize angle distortion.

    Uses gradient descent to minimize the conformal energy.

    Args:
        vertices: (N, 3) array of vertex positions
        triangles: (M, 3) array of triangle indices
        uvs_init: (N, 2) initial UV coordinates
        max_iter: Maximum number of optimization iterations

    Returns:
        (N, 2) optimized UV coordinates
    """
    def conformal_energy(uvs_flat):
        uvs = uvs_flat.reshape(-1, 2)
        energy = 0.0

        for tri in triangles:
            v0, v1, v2 = tri

            # 3D edges
            e1_3d = vertices[v1] - vertices[v0]
            e2_3d = vertices[v2] - vertices[v0]

            # 2D edges
            e1_2d = uvs[v1] - uvs[v0]
            e2_2d = uvs[v2] - uvs[v0]

            # Jacobian
            J = np.column_stack([e1_2d, e2_2d])

            # Conformal energy (Frobenius norm of Jacobian deviation)
            energy += np.linalg.norm(J - J.T)**2

        return energy

    # Optimize
    result = minimize(
        conformal_energy,
        uvs_init.flatten(),
        method='L-BFGS-B',
        bounds=[(0, 1)] * (len(uvs_init) * 2),
        options={'maxiter': max_iter}
    )

    return result.x.reshape(-1, 2)


def compute_uv_bounding_box(uvs: np.ndarray) -> tuple:
    """
    Compute bounding box of UV coordinates.

    Args:
        uvs: (N, 2) UV coordinates

    Returns:
        (u_min, v_min, u_max, v_max)
    """
    u_min = np.min(uvs[:, 0])
    v_min = np.min(uvs[:, 1])
    u_max = np.max(uvs[:, 0])
    v_max = np.max(uvs[:, 1])

    return (u_min, v_min, u_max, v_max)


def normalize_uvs_to_unit_square(uvs: np.ndarray) -> np.ndarray:
    """
    Normalize UV coordinates to [0, 1]² while preserving aspect ratio.

    Args:
        uvs: (N, 2) UV coordinates

    Returns:
        (N, 2) normalized UV coordinates
    """
    u_min, v_min, u_max, v_max = compute_uv_bounding_box(uvs)

    # Scale to unit square
    u_range = u_max - u_min
    v_range = v_max - v_min

    if u_range < 1e-10 or v_range < 1e-10:
        return uvs

    uvs_normalized = (uvs - np.array([u_min, v_min])) / np.array([u_range, v_range])

    return uvs_normalized
