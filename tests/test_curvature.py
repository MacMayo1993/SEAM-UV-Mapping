"""
Tests for Gaussian curvature computation.
"""

import numpy as np

from addon.core.curvature import compute_gaussian_curvature, compute_mean_curvature


class TestGaussianCurvature:
    """Test suite for Gaussian curvature computation"""

    def test_sphere_positive_curvature(self, sphere_mesh_simple):
        """Sphere should have positive curvature everywhere"""
        vertices, triangles = sphere_mesh_simple

        K = compute_gaussian_curvature(vertices, triangles)

        # All curvatures should be positive
        assert np.all(K > 0), "Sphere has negative curvature"

        # Should integrate to 4π (Gauss-Bonnet for sphere)
        # Total curvature ≈ 4π (accounting for discretization)
        total_K = np.sum(K)
        expected = 4 * np.pi
        assert (
            abs(total_K - expected) < 1.0
        ), f"Sphere curvature should integrate to 4π, got {total_K:.2f}"

    def test_plane_zero_curvature(self, plane_mesh):
        """Flat plane should have zero curvature"""
        vertices, triangles = plane_mesh

        K = compute_gaussian_curvature(vertices, triangles)

        # All curvatures should be near zero
        assert np.allclose(K, 0.0, atol=1e-6), f"Plane should have zero curvature, got {K}"

    def test_cylinder_mixed_curvature(self, cylinder_mesh):
        """Cylinder should have zero Gaussian curvature (developable surface)"""
        vertices, triangles = cylinder_mesh

        K = compute_gaussian_curvature(vertices, triangles)

        # Gaussian curvature of cylinder is 0 (one principal curvature is 0)
        assert np.allclose(K, 0.0, atol=0.1), "Cylinder should have near-zero Gaussian curvature"

    def test_curvature_dimension(self, sphere_mesh_simple):
        """Curvature output should match number of vertices"""
        vertices, triangles = sphere_mesh_simple

        K = compute_gaussian_curvature(vertices, triangles)

        assert K.shape == (
            len(vertices),
        ), f"Expected {len(vertices)} curvature values, got {len(K)}"

    def test_curvature_finite(self, sphere_mesh_simple):
        """Curvature values should be finite"""
        vertices, triangles = sphere_mesh_simple

        K = compute_gaussian_curvature(vertices, triangles)

        assert np.all(np.isfinite(K)), "Curvature contains NaN or inf"

    def test_degenerate_triangle(self):
        """Handle degenerate triangle (zero area)"""
        vertices = np.array(
            [
                [0, 0, 0],
                [1, 0, 0],
                [2, 0, 0],  # Colinear
            ],
            dtype=np.float64,
        )

        triangles = np.array([[0, 1, 2]], dtype=np.int32)

        K = compute_gaussian_curvature(vertices, triangles)

        # Should handle gracefully (may be zero or small)
        assert np.all(np.isfinite(K)), "Degenerate triangle causes NaN"


class TestMeanCurvature:
    """Test suite for mean curvature computation"""

    def test_sphere_constant_mean_curvature(self, sphere_mesh_simple):
        """Sphere of radius 1 should have mean curvature = 1"""
        vertices, triangles = sphere_mesh_simple

        H = compute_mean_curvature(vertices, triangles)

        # Mean curvature should be approximately 1 for unit sphere
        # (May vary due to discretization)
        assert np.mean(np.abs(H)) > 0.5, "Mean curvature too small"
        assert np.mean(np.abs(H)) < 2.0, "Mean curvature too large"

    def test_plane_zero_mean_curvature(self, plane_mesh):
        """Plane should have zero mean curvature"""
        vertices, triangles = plane_mesh

        H = compute_mean_curvature(vertices, triangles)

        assert np.allclose(H, 0.0, atol=0.1), "Plane should have near-zero mean curvature"


class TestCurvatureEdgeCases:
    """Test edge cases and error handling"""

    def test_single_triangle(self):
        """Single triangle mesh"""
        vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float64)

        triangles = np.array([[0, 1, 2]], dtype=np.int32)

        K = compute_gaussian_curvature(vertices, triangles)

        # Should run without error
        assert len(K) == 3

    def test_empty_mesh(self):
        """Empty mesh should handle gracefully"""
        vertices = np.empty((0, 3), dtype=np.float64)
        triangles = np.empty((0, 3), dtype=np.int32)

        K = compute_gaussian_curvature(vertices, triangles)

        assert len(K) == 0

    def test_isolated_vertex(self):
        """Vertex not in any triangle"""
        vertices = np.array(
            [
                [0, 0, 0],
                [1, 0, 0],
                [0, 1, 0],
                [10, 10, 10],  # Isolated
            ],
            dtype=np.float64,
        )

        triangles = np.array([[0, 1, 2]], dtype=np.int32)

        K = compute_gaussian_curvature(vertices, triangles)

        # Isolated vertex should have curvature = 2π (angle deficit)
        assert abs(K[3] - 2 * np.pi) < 0.1, "Isolated vertex should have curvature 2π"
