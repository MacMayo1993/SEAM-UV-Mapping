"""
Main topological UV atlas implementation.

This module orchestrates the entire non-orientable UV unwrapping algorithm.
"""

import numpy as np
from typing import Set, Tuple, Dict, Optional
from collections import defaultdict

from .curvature import compute_gaussian_curvature
from .parity import assign_parity
from .uv_generation import generate_uvs


class TopologicalUVAtlas:
    """
    Non-orientable UV atlas using orientation parity tracking.

    This class implements the complete algorithm:
    1. Compute Gaussian curvature at each vertex
    2. Score edges by curvature jump (ΔMDL)
    3. Select top k* fraction as stitch edges
    4. Flood-fill parity assignment (±1)
    5. Generate UV coordinates with antipodal correction

    Attributes:
        vertices (np.ndarray): (N, 3) vertex positions
        triangles (np.ndarray): (M, 3) triangle indices
        k_star (float): Stitch edge selection threshold [0, 1]
        vertex_uvs (np.ndarray): (N, 2) UV coordinates
        vertex_parities (np.ndarray): (N,) parity values ±1
        stitch_edges (Set): Set of (v1, v2) edge tuples where parity flips
    """

    def __init__(
        self,
        vertices: np.ndarray,
        triangles: np.ndarray,
        k_star: float = 0.721,
        verbose: bool = False
    ):
        """
        Initialize and compute topological UV atlas.

        Args:
            vertices: (N, 3) array of vertex positions
            triangles: (M, 3) array of triangle indices
            k_star: Stitch edge selection threshold (default: 0.721)
            verbose: Print progress messages

        Raises:
            ValueError: If mesh is non-manifold or has invalid topology
        """
        self.vertices = vertices
        self.triangles = triangles
        self.k_star = k_star
        self.verbose = verbose

        # Validate input
        self._validate_mesh()

        # Build connectivity
        self._build_connectivity()

        # Run algorithm
        self._compute_unwrapping()

    def _validate_mesh(self):
        """Validate mesh topology before unwrapping."""
        if self.vertices.ndim != 2 or self.vertices.shape[1] != 3:
            raise ValueError(f"Expected (N, 3) vertices, got {self.vertices.shape}")

        if self.triangles.ndim != 2 or self.triangles.shape[1] != 3:
            raise ValueError(f"Expected (M, 3) triangles, got {self.triangles.shape}")

        if self.k_star < 0.0 or self.k_star > 1.0:
            raise ValueError(f"k_star must be in [0, 1], got {self.k_star}")

        # Check for valid indices
        if np.any(self.triangles < 0) or np.any(self.triangles >= len(self.vertices)):
            raise ValueError("Triangle indices out of bounds")

    def _build_connectivity(self):
        """Build edge-to-triangle and vertex-to-triangle connectivity."""
        self.edge_to_tris = defaultdict(list)
        self.vertex_to_tris = defaultdict(list)

        for tri_idx, tri in enumerate(self.triangles):
            v0, v1, v2 = tri

            # Add edges (sorted for consistency)
            edges = [
                tuple(sorted([v0, v1])),
                tuple(sorted([v1, v2])),
                tuple(sorted([v2, v0]))
            ]

            for edge in edges:
                self.edge_to_tris[edge].append(tri_idx)

            # Add vertex adjacency
            for v in tri:
                self.vertex_to_tris[v].append(tri_idx)

        # Check manifoldness
        for edge, tris in self.edge_to_tris.items():
            if len(tris) > 2:
                raise ValueError(
                    f"Non-manifold mesh: edge {edge} has {len(tris)} adjacent faces. "
                    "Each edge must have exactly 1 or 2 adjacent faces."
                )

        self.edges = list(self.edge_to_tris.keys())

        if self.verbose:
            print(f"Built connectivity: {len(self.vertices)} vertices, "
                  f"{len(self.triangles)} triangles, {len(self.edges)} edges")

    def _compute_unwrapping(self):
        """Main algorithm: compute UV unwrapping with parity."""
        # Step 1: Compute Gaussian curvature
        if self.verbose:
            print("Computing Gaussian curvature...")

        self.curvatures = compute_gaussian_curvature(self.vertices, self.triangles)

        # Step 2: Score edges by curvature jump
        if self.verbose:
            print("Scoring edges...")

        edge_scores = self._compute_edge_scores()

        # Step 3: Select stitch edges (top k* fraction)
        if self.verbose:
            print(f"Selecting stitch edges (k* = {self.k_star})...")

        self.stitch_edges = self._select_stitch_edges(edge_scores)

        if self.verbose:
            print(f"Selected {len(self.stitch_edges)} stitch edges "
                  f"({100 * len(self.stitch_edges) / len(self.edges):.1f}%)")

        # Step 4: Assign parity
        if self.verbose:
            print("Assigning parity...")

        self.tri_parity = assign_parity(
            self.triangles,
            self.stitch_edges,
            self.edge_to_tris
        )

        # Convert to vertex parity (majority vote)
        self.vertex_parities = self._tri_to_vertex_parity()

        # Step 5: Generate UVs
        if self.verbose:
            print("Generating UV coordinates...")

        self.vertex_uvs = generate_uvs(
            self.vertices,
            self.triangles,
            self.vertex_parities
        )

        if self.verbose:
            print("UV unwrapping complete!")

    def _compute_edge_scores(self) -> np.ndarray:
        """
        Compute edge importance scores using curvature jump (ΔMDL).

        Returns:
            Array of scores for each edge (higher = more important)
        """
        scores = np.zeros(len(self.edges))

        for i, edge in enumerate(self.edges):
            v1, v2 = edge
            K1 = self.curvatures[v1]
            K2 = self.curvatures[v2]

            # Normalized curvature jump
            delta_K = abs(K1 - K2)
            avg_K = (abs(K1) + abs(K2)) / 2.0

            # Avoid division by zero
            if avg_K > 1e-10:
                scores[i] = delta_K / avg_K
            else:
                scores[i] = 0.0

        return scores

    def _select_stitch_edges(self, edge_scores: np.ndarray) -> Set[Tuple[int, int]]:
        """
        Select top k* fraction of edges as stitch edges.

        Args:
            edge_scores: Array of edge importance scores

        Returns:
            Set of edge tuples that are stitch edges
        """
        # Sort edges by score (descending)
        sorted_indices = np.argsort(edge_scores)[::-1]

        # Select top k* fraction
        num_stitch = int(self.k_star * len(self.edges))
        stitch_indices = sorted_indices[:num_stitch]

        stitch_edges = set()
        for idx in stitch_indices:
            stitch_edges.add(self.edges[idx])

        return stitch_edges

    def _tri_to_vertex_parity(self) -> np.ndarray:
        """
        Convert triangle parity to vertex parity (majority vote).

        Returns:
            (N,) array of vertex parities ±1
        """
        vertex_parities = np.zeros(len(self.vertices))

        for v in range(len(self.vertices)):
            # Get adjacent triangles
            adj_tris = self.vertex_to_tris[v]

            # Majority vote
            parity_sum = sum(self.tri_parity[t] for t in adj_tris)
            vertex_parities[v] = 1 if parity_sum >= 0 else -1

        return vertex_parities.astype(np.int32)

    def get_stats(self) -> Dict[str, float]:
        """
        Get statistics about the unwrapping.

        Returns:
            Dictionary with statistics
        """
        return {
            "num_vertices": len(self.vertices),
            "num_triangles": len(self.triangles),
            "num_edges": len(self.edges),
            "num_stitch_edges": len(self.stitch_edges),
            "stitch_fraction": len(self.stitch_edges) / len(self.edges),
            "k_star": self.k_star,
            "curvature_mean": float(np.mean(np.abs(self.curvatures))),
            "curvature_max": float(np.max(np.abs(self.curvatures))),
        }
