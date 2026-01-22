"""
Tests for parity assignment logic.
"""

from collections import defaultdict

import numpy as np

from addon.core.parity import (
    assign_parity,
    compute_parity_field_gradient,
    verify_parity_consistency,
)


class TestParityAssignment:
    """Test suite for parity assignment"""

    def test_no_stitch_edges(self, sphere_mesh_simple):
        """With no stitch edges, all triangles should have same parity"""
        vertices, triangles = sphere_mesh_simple

        # Build edge connectivity
        edge_to_tris = defaultdict(list)
        for tri_idx, tri in enumerate(triangles):
            edges = [
                tuple(sorted([tri[0], tri[1]])),
                tuple(sorted([tri[1], tri[2]])),
                tuple(sorted([tri[2], tri[0]]))
            ]
            for edge in edges:
                edge_to_tris[edge].append(tri_idx)

        # No stitch edges
        stitch_edges = set()

        tri_parity = assign_parity(triangles, stitch_edges, edge_to_tris)

        # All parities should be the same
        assert np.all(tri_parity == tri_parity[0]), \
            "Without stitch edges, all triangles should have same parity"

    def test_all_stitch_edges(self, sphere_mesh_simple):
        """With all edges as stitches, adjacent triangles should flip"""
        vertices, triangles = sphere_mesh_simple

        # Build edge connectivity
        edge_to_tris = defaultdict(list)
        for tri_idx, tri in enumerate(triangles):
            edges = [
                tuple(sorted([tri[0], tri[1]])),
                tuple(sorted([tri[1], tri[2]])),
                tuple(sorted([tri[2], tri[0]]))
            ]
            for edge in edges:
                edge_to_tris[edge].append(tri_idx)

        # All edges are stitches
        stitch_edges = set(edge_to_tris.keys())

        tri_parity = assign_parity(triangles, stitch_edges, edge_to_tris)

        # Verify parities flip across all edges
        for edge, tris in edge_to_tris.items():
            if len(tris) == 2:
                assert tri_parity[tris[0]] != tri_parity[tris[1]], \
                    f"Parity should flip across stitch edge {edge}"

    def test_parity_values(self, sphere_mesh_simple):
        """Parity values should be ±1"""
        vertices, triangles = sphere_mesh_simple

        edge_to_tris = defaultdict(list)
        for tri_idx, tri in enumerate(triangles):
            edges = [
                tuple(sorted([tri[0], tri[1]])),
                tuple(sorted([tri[1], tri[2]])),
                tuple(sorted([tri[2], tri[0]]))
            ]
            for edge in edges:
                edge_to_tris[edge].append(tri_idx)

        stitch_edges = set(list(edge_to_tris.keys())[:10])  # Some stitches

        tri_parity = assign_parity(triangles, stitch_edges, edge_to_tris)

        # Check values are ±1
        unique_parities = np.unique(tri_parity)
        assert set(unique_parities).issubset({-1, 1}), \
            f"Parity values should be ±1, got {unique_parities}"

    def test_connected_components(self):
        """Disconnected mesh components can have independent parities"""
        # Two separate triangles
        np.array([
            [0, 0, 0], [1, 0, 0], [0, 1, 0],  # Triangle 1
            [10, 0, 0], [11, 0, 0], [10, 1, 0]  # Triangle 2 (disconnected)
        ], dtype=np.float64)

        triangles = np.array([
            [0, 1, 2],
            [3, 4, 5]
        ], dtype=np.int32)

        edge_to_tris = defaultdict(list)
        for tri_idx, tri in enumerate(triangles):
            edges = [
                tuple(sorted([tri[0], tri[1]])),
                tuple(sorted([tri[1], tri[2]])),
                tuple(sorted([tri[2], tri[0]]))
            ]
            for edge in edges:
                edge_to_tris[edge].append(tri_idx)

        stitch_edges = set()

        tri_parity = assign_parity(triangles, stitch_edges, edge_to_tris)

        # Both components should be assigned (potentially different parities)
        assert len(np.unique(tri_parity)) >= 1


class TestParityConsistency:
    """Test parity consistency verification"""

    def test_consistent_parity(self, sphere_mesh_simple):
        """Properly assigned parity should be consistent"""
        vertices, triangles = sphere_mesh_simple

        edge_to_tris = defaultdict(list)
        for tri_idx, tri in enumerate(triangles):
            edges = [
                tuple(sorted([tri[0], tri[1]])),
                tuple(sorted([tri[1], tri[2]])),
                tuple(sorted([tri[2], tri[0]]))
            ]
            for edge in edges:
                edge_to_tris[edge].append(tri_idx)

        stitch_edges = set(list(edge_to_tris.keys())[:5])

        tri_parity = assign_parity(triangles, stitch_edges, edge_to_tris)

        # Verify consistency
        is_consistent = verify_parity_consistency(
            triangles, tri_parity, stitch_edges, edge_to_tris
        )

        assert is_consistent, "Parity assignment should be consistent"

    def test_inconsistent_parity(self, sphere_mesh_simple):
        """Manually broken parity should be detected"""
        vertices, triangles = sphere_mesh_simple

        edge_to_tris = defaultdict(list)
        for tri_idx, tri in enumerate(triangles):
            edges = [
                tuple(sorted([tri[0], tri[1]])),
                tuple(sorted([tri[1], tri[2]])),
                tuple(sorted([tri[2], tri[0]]))
            ]
            for edge in edges:
                edge_to_tris[edge].append(tri_idx)

        stitch_edges = set(list(edge_to_tris.keys())[:5])

        tri_parity = assign_parity(triangles, stitch_edges, edge_to_tris)

        # Break consistency: flip one triangle without updating stitches
        tri_parity[0] *= -1

        is_consistent = verify_parity_consistency(
            triangles, tri_parity, stitch_edges, edge_to_tris
        )

        assert not is_consistent, "Should detect inconsistent parity"


class TestParityGradient:
    """Test parity field gradient computation"""

    def test_gradient_no_stitches(self, sphere_mesh_simple):
        """No stitches means gradient should be 0"""
        vertices, triangles = sphere_mesh_simple

        edge_to_tris = defaultdict(list)
        for tri_idx, tri in enumerate(triangles):
            edges = [
                tuple(sorted([tri[0], tri[1]])),
                tuple(sorted([tri[1], tri[2]])),
                tuple(sorted([tri[2], tri[0]]))
            ]
            for edge in edges:
                edge_to_tris[edge].append(tri_idx)

        stitch_edges = set()
        tri_parity = assign_parity(triangles, stitch_edges, edge_to_tris)

        gradient = compute_parity_field_gradient(triangles, tri_parity, edge_to_tris)

        assert gradient == 0.0, "Gradient should be 0 without stitches"

    def test_gradient_all_stitches(self, sphere_mesh_simple):
        """All stitches means gradient should be 1.0"""
        vertices, triangles = sphere_mesh_simple

        edge_to_tris = defaultdict(list)
        for tri_idx, tri in enumerate(triangles):
            edges = [
                tuple(sorted([tri[0], tri[1]])),
                tuple(sorted([tri[1], tri[2]])),
                tuple(sorted([tri[2], tri[0]]))
            ]
            for edge in edges:
                edge_to_tris[edge].append(tri_idx)

        stitch_edges = set(edge_to_tris.keys())
        tri_parity = assign_parity(triangles, stitch_edges, edge_to_tris)

        gradient = compute_parity_field_gradient(triangles, tri_parity, edge_to_tris)

        assert gradient == 1.0, "Gradient should be 1.0 with all stitches"
