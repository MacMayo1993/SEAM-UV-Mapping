"""
Gaussian curvature computation using discrete angle deficit method.

For closed polyhedral surfaces, the Gaussian curvature at a vertex is:
    K = 2π - Σ(angles at vertex)

This is known as the angle deficit formula.
"""

from collections import defaultdict

import numpy as np


def compute_gaussian_curvature(
    vertices: np.ndarray,
    triangles: np.ndarray
) -> np.ndarray:
    """
    Compute discrete Gaussian curvature at each vertex using angle deficit.

    The angle deficit at a vertex v is:
        K(v) = 2π - Σ θᵢ
    where θᵢ are the angles at v in adjacent triangles.

    Args:
        vertices: (N, 3) array of vertex positions
        triangles: (M, 3) array of triangle indices

    Returns:
        (N,) array of Gaussian curvature values in radians

    References:
        - Meyer et al. "Discrete Differential-Geometry Operators for
          Triangulated 2-Manifolds" (2003)
    """
    num_vertices = len(vertices)
    curvatures = np.full(num_vertices, 2.0 * np.pi)  # Start with 2π

    # Build vertex-to-triangles adjacency
    vertex_to_tris = defaultdict(list)
    for tri_idx, tri in enumerate(triangles):
        for v in tri:
            vertex_to_tris[v].append(tri_idx)

    # Subtract angles at each vertex
    for tri in triangles:
        v0, v1, v2 = tri

        # Get positions
        p0 = vertices[v0]
        p1 = vertices[v1]
        p2 = vertices[v2]

        # Compute angles at each vertex
        angle0 = _compute_angle(p1 - p0, p2 - p0)
        angle1 = _compute_angle(p0 - p1, p2 - p1)
        angle2 = _compute_angle(p0 - p2, p1 - p2)

        # Subtract from angle deficit
        curvatures[v0] -= angle0
        curvatures[v1] -= angle1
        curvatures[v2] -= angle2

    return curvatures


def _compute_angle(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Compute angle between two vectors.

    Args:
        v1: First vector
        v2: Second vector

    Returns:
        Angle in radians [0, π]
    """
    # Normalize vectors
    v1_norm = np.linalg.norm(v1)
    v2_norm = np.linalg.norm(v2)

    if v1_norm < 1e-10 or v2_norm < 1e-10:
        return 0.0

    v1_unit = v1 / v1_norm
    v2_unit = v2 / v2_norm

    # Compute angle via dot product
    cos_angle = np.dot(v1_unit, v2_unit)

    # Clamp to avoid numerical issues
    cos_angle = np.clip(cos_angle, -1.0, 1.0)

    return np.arccos(cos_angle)


def compute_mean_curvature(
    vertices: np.ndarray,
    triangles: np.ndarray
) -> np.ndarray:
    """
    Compute discrete mean curvature at each vertex.

    Uses cotangent formula. This is optional and not used in the main algorithm,
    but provided for completeness.

    Args:
        vertices: (N, 3) array of vertex positions
        triangles: (M, 3) array of triangle indices

    Returns:
        (N,) array of mean curvature values
    """
    num_vertices = len(vertices)
    mean_curvatures = np.zeros(num_vertices)
    vertex_areas = np.zeros(num_vertices)

    # Build edges
    edges = set()
    for tri in triangles:
        v0, v1, v2 = tri
        edges.add(tuple(sorted([v0, v1])))
        edges.add(tuple(sorted([v1, v2])))
        edges.add(tuple(sorted([v2, v0])))

    # Compute cotangent weights for each edge
    for v1, v2 in edges:
        # Find triangles sharing this edge
        edge_tris = []
        for tri in triangles:
            if v1 in tri and v2 in tri:
                edge_tris.append(tri)

        if len(edge_tris) != 2:
            continue  # Boundary edge

        # Compute cotangent weights
        cot_sum = 0.0
        for tri in edge_tris:
            # Find opposite vertex
            v_opp = [v for v in tri if v != v1 and v != v2][0]

            p1 = vertices[v1]
            p2 = vertices[v2]
            p_opp = vertices[v_opp]

            # Vectors from opposite vertex
            e1 = p1 - p_opp
            e2 = p2 - p_opp

            # Cotangent = cos/sin
            cos_angle = np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2))
            sin_angle = np.sqrt(1.0 - cos_angle**2)

            if sin_angle > 1e-10:
                cot_sum += cos_angle / sin_angle

        # Laplacian operator
        edge_vec = vertices[v2] - vertices[v1]
        mean_curvatures[v1] += 0.5 * cot_sum * np.linalg.norm(edge_vec)
        mean_curvatures[v2] += 0.5 * cot_sum * np.linalg.norm(edge_vec)

    # Compute vertex areas (Voronoi regions)
    for tri in triangles:
        v0, v1, v2 = tri
        area = _compute_triangle_area(vertices[v0], vertices[v1], vertices[v2])

        # Distribute area to vertices
        vertex_areas[v0] += area / 3.0
        vertex_areas[v1] += area / 3.0
        vertex_areas[v2] += area / 3.0

    # Normalize by area
    mean_curvatures = np.divide(
        mean_curvatures,
        vertex_areas,
        where=vertex_areas > 1e-10
    )

    return mean_curvatures


def _compute_triangle_area(p0: np.ndarray, p1: np.ndarray, p2: np.ndarray) -> float:
    """
    Compute area of triangle using cross product.

    Args:
        p0, p1, p2: Vertex positions

    Returns:
        Triangle area
    """
    v1 = p1 - p0
    v2 = p2 - p0
    cross = np.cross(v1, v2)
    return 0.5 * np.linalg.norm(cross)
