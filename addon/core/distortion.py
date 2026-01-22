"""
Distortion metrics for UV parameterizations.

Provides functions to measure angle distortion, area distortion,
and UV space coverage.
"""

import numpy as np


def compute_angle_distortion(
    vertices: np.ndarray, triangles: np.ndarray, uvs: np.ndarray
) -> dict[str, float]:
    """
    Compute angle distortion between 3D mesh and 2D UV layout.

    Angle distortion measures how much angles are distorted during
    the parameterization. For a conformal map, this should be zero.

    Args:
        vertices: (N, 3) vertex positions
        triangles: (M, 3) triangle indices
        uvs: (N, 2) UV coordinates

    Returns:
        Dictionary with keys:
            - mean: Mean angle distortion in degrees
            - max: Maximum angle distortion in degrees
            - std: Standard deviation in degrees
    """
    angle_distortions = []

    for tri in triangles:
        v0, v1, v2 = tri

        # Compute angles in 3D
        p0, p1, p2 = vertices[v0], vertices[v1], vertices[v2]
        angle_3d_0 = _compute_angle(p1 - p0, p2 - p0)
        angle_3d_1 = _compute_angle(p0 - p1, p2 - p1)
        angle_3d_2 = _compute_angle(p0 - p2, p1 - p2)

        # Compute angles in 2D UV
        uv0, uv1, uv2 = uvs[v0], uvs[v1], uvs[v2]
        angle_2d_0 = _compute_angle(uv1 - uv0, uv2 - uv0)
        angle_2d_1 = _compute_angle(uv0 - uv1, uv2 - uv1)
        angle_2d_2 = _compute_angle(uv0 - uv2, uv1 - uv2)

        # Angular distortion (in radians)
        dist_0 = abs(angle_3d_0 - angle_2d_0)
        dist_1 = abs(angle_3d_1 - angle_2d_1)
        dist_2 = abs(angle_3d_2 - angle_2d_2)

        angle_distortions.extend([dist_0, dist_1, dist_2])

    # Convert to degrees
    angle_distortions = np.array(angle_distortions) * 180.0 / np.pi

    return {
        "mean": float(np.mean(angle_distortions)),
        "max": float(np.max(angle_distortions)),
        "std": float(np.std(angle_distortions)),
    }


def compute_area_distortion(vertices: np.ndarray, triangles: np.ndarray, uvs: np.ndarray) -> float:
    """
    Compute area distortion (stretch) metric.

    Measures the ratio of maximum to minimum area scaling across all triangles.
    For an equiareal (authalic) map, this should be 1.0.

    Args:
        vertices: (N, 3) vertex positions
        triangles: (M, 3) triangle indices
        uvs: (N, 2) UV coordinates

    Returns:
        Area distortion metric (max/min area ratio)
    """
    area_ratios = []

    for tri in triangles:
        v0, v1, v2 = tri

        # 3D triangle area
        p0, p1, p2 = vertices[v0], vertices[v1], vertices[v2]
        area_3d = _compute_triangle_area_3d(p0, p1, p2)

        # 2D UV triangle area
        uv0, uv1, uv2 = uvs[v0], uvs[v1], uvs[v2]
        area_2d = _compute_triangle_area_2d(uv0, uv1, uv2)

        # Avoid division by zero
        if area_3d > 1e-10 and area_2d > 1e-10:
            ratio = area_2d / area_3d
            area_ratios.append(ratio)

    if not area_ratios:
        return 1.0

    area_ratios = np.array(area_ratios)
    max_ratio = np.max(area_ratios)
    min_ratio = np.min(area_ratios)

    # Distortion = max / min
    distortion = max_ratio / min_ratio if min_ratio > 1e-10 else float("inf")

    return float(distortion)


def compute_uv_coverage(triangles: np.ndarray, uvs: np.ndarray) -> float:
    """
    Compute UV space utilization (coverage percentage).

    Measures what fraction of the [0, 1]² UV square is occupied by triangles.

    Args:
        triangles: (M, 3) triangle indices
        uvs: (N, 2) UV coordinates

    Returns:
        Coverage percentage (0-100)
    """
    # Compute total UV area
    total_area = 0.0

    for tri in triangles:
        v0, v1, v2 = tri
        uv0, uv1, uv2 = uvs[v0], uvs[v1], uvs[v2]
        area = _compute_triangle_area_2d(uv0, uv1, uv2)
        total_area += area

    # UV space is [0, 1]², so max area = 1.0
    coverage = (total_area / 1.0) * 100.0

    return float(coverage)


def compute_stretch_metric(
    vertices: np.ndarray, triangles: np.ndarray, uvs: np.ndarray
) -> dict[str, float]:
    """
    Compute stretch distortion (singular values of Jacobian).

    Args:
        vertices: (N, 3) vertex positions
        triangles: (M, 3) triangle indices
        uvs: (N, 2) UV coordinates

    Returns:
        Dictionary with mean and max stretch values
    """
    stretches = []

    for tri in triangles:
        v0, v1, v2 = tri

        # 3D edges
        p0, p1, p2 = vertices[v0], vertices[v1], vertices[v2]
        e1_3d = p1 - p0
        e2_3d = p2 - p0

        # 2D UV edges
        uv0, uv1, uv2 = uvs[v0], uvs[v1], uvs[v2]
        e1_2d = uv1 - uv0
        e2_2d = uv2 - uv0

        # Compute Jacobian (least squares)
        # J maps 2D UV to 3D surface tangent
        A = np.column_stack([e1_2d, e2_2d])
        B = np.column_stack([e1_3d, e2_3d])

        if np.linalg.det(A) > 1e-10:
            J = B @ np.linalg.inv(A)

            # Singular values = stretch factors
            svd = np.linalg.svd(J, compute_uv=False)
            max_stretch = np.max(svd)
            stretches.append(max_stretch)

    if not stretches:
        return {"mean": 1.0, "max": 1.0}

    return {"mean": float(np.mean(stretches)), "max": float(np.max(stretches))}


# Helper functions


def _compute_angle(v1: np.ndarray, v2: np.ndarray) -> float:
    """Compute angle between two vectors."""
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)

    if norm1 < 1e-10 or norm2 < 1e-10:
        return 0.0

    cos_angle = np.dot(v1, v2) / (norm1 * norm2)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)

    return np.arccos(cos_angle)


def _compute_triangle_area_3d(p0: np.ndarray, p1: np.ndarray, p2: np.ndarray) -> float:
    """Compute 3D triangle area using cross product."""
    v1 = p1 - p0
    v2 = p2 - p0
    cross = np.cross(v1, v2)
    return 0.5 * np.linalg.norm(cross)


def _compute_triangle_area_2d(uv0: np.ndarray, uv1: np.ndarray, uv2: np.ndarray) -> float:
    """Compute 2D triangle area using cross product."""
    v1 = uv1 - uv0
    v2 = uv2 - uv0

    # 2D cross product (scalar)
    cross = v1[0] * v2[1] - v1[1] * v2[0]
    return 0.5 * abs(cross)
