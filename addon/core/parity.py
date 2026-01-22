"""
Parity assignment via flood-fill across stitch edges.

Each triangle is assigned a parity σ ∈ {+1, -1}, representing its orientation
in the orientable double cover. Parity flips when crossing a stitch edge.
"""

from collections import defaultdict, deque

import numpy as np


def assign_parity(
    triangles: np.ndarray,
    stitch_edges: set[tuple[int, int]],
    edge_to_tris: dict[tuple[int, int], list[int]]
) -> np.ndarray:
    """
    Assign parity to each triangle via flood-fill.

    Starting from an arbitrary triangle with parity +1, flood-fill to adjacent
    triangles. When crossing a stitch edge, flip the parity.

    Args:
        triangles: (M, 3) array of triangle indices
        stitch_edges: Set of edge tuples that are stitch edges
        edge_to_tris: Dictionary mapping edges to adjacent triangle indices

    Returns:
        (M,) array of triangle parities ±1
    """
    num_triangles = len(triangles)
    tri_parity = np.zeros(num_triangles, dtype=np.int32)
    visited = np.zeros(num_triangles, dtype=bool)

    # Build triangle-to-triangle adjacency
    tri_to_tris = defaultdict(set)
    for edge, tris in edge_to_tris.items():
        if len(tris) == 2:
            t1, t2 = tris
            is_stitch = edge in stitch_edges
            tri_to_tris[t1].add((t2, is_stitch))
            tri_to_tris[t2].add((t1, is_stitch))

    # Flood-fill from each component
    for start_tri in range(num_triangles):
        if visited[start_tri]:
            continue

        # BFS from this triangle
        queue = deque([start_tri])
        tri_parity[start_tri] = 1  # Arbitrary starting parity
        visited[start_tri] = True

        while queue:
            current = queue.popleft()
            current_parity = tri_parity[current]

            # Visit adjacent triangles
            for neighbor, is_stitch in tri_to_tris[current]:
                if visited[neighbor]:
                    continue

                # Assign parity (flip if crossing stitch)
                if is_stitch:
                    tri_parity[neighbor] = -current_parity
                else:
                    tri_parity[neighbor] = current_parity

                visited[neighbor] = True
                queue.append(neighbor)

    return tri_parity


def verify_parity_consistency(
    triangles: np.ndarray,
    tri_parity: np.ndarray,
    stitch_edges: set[tuple[int, int]],
    edge_to_tris: dict[tuple[int, int], list[int]]
) -> bool:
    """
    Verify that parity assignment is consistent.

    Across stitch edges, parity should flip. Across non-stitch edges,
    parity should be consistent.

    Args:
        triangles: (M, 3) array of triangle indices
        tri_parity: (M,) array of triangle parities
        stitch_edges: Set of stitch edges
        edge_to_tris: Edge-to-triangle adjacency

    Returns:
        True if parity assignment is consistent
    """
    for edge, tris in edge_to_tris.items():
        if len(tris) != 2:
            continue  # Boundary edge

        t1, t2 = tris
        p1 = tri_parity[t1]
        p2 = tri_parity[t2]

        is_stitch = edge in stitch_edges

        if is_stitch:
            # Should flip
            if p1 == p2:
                return False
        else:
            # Should not flip
            if p1 != p2:
                return False

    return True


def compute_parity_field_gradient(
    triangles: np.ndarray,
    tri_parity: np.ndarray,
    edge_to_tris: dict[tuple[int, int], list[int]]
) -> float:
    """
    Compute gradient of parity field (number of parity flips).

    This measures how many edges have parity discontinuities.

    Args:
        triangles: (M, 3) array of triangle indices
        tri_parity: (M,) array of triangle parities
        edge_to_tris: Edge-to-triangle adjacency

    Returns:
        Fraction of edges with parity flips
    """
    num_flips = 0
    num_edges = 0

    for edge, tris in edge_to_tris.items():
        if len(tris) != 2:
            continue

        t1, t2 = tris
        if tri_parity[t1] != tri_parity[t2]:
            num_flips += 1

        num_edges += 1

    return num_flips / num_edges if num_edges > 0 else 0.0
