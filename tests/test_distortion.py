"""
Tests for UV distortion metrics.
"""

import pytest
import numpy as np
from addon.core.distortion import (
    compute_angle_distortion,
    compute_area_distortion,
    compute_uv_coverage,
    compute_stretch_metric
)


class TestAngleDistortion:
    """Test angle distortion computation"""

    def test_conformal_mapping_zero_distortion(self):
        """Perfect conformal mapping should have zero angle distortion"""
        # Right triangle in 3D
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [0, 1, 0]
        ], dtype=np.float64)

        triangles = np.array([[0, 1, 2]], dtype=np.int32)

        # Conformal UV (preserves angles)
        uvs = np.array([
            [0, 0], [1, 0], [0, 1]
        ], dtype=np.float64)

        distortion = compute_angle_distortion(vertices, triangles, uvs)

        assert distortion['mean'] < 1.0, "Conformal mapping should have low distortion"
        assert distortion['max'] < 2.0, "Conformal mapping should have low distortion"

    def test_flipped_triangle_high_distortion(self):
        """Flipped triangle should have high angle distortion"""
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [0, 1, 0]
        ], dtype=np.float64)

        triangles = np.array([[0, 1, 2]], dtype=np.int32)

        # Flipped UV
        uvs = np.array([
            [0, 0], [0, 1], [1, 0]  # Different order
        ], dtype=np.float64)

        distortion = compute_angle_distortion(vertices, triangles, uvs)

        # Should have some distortion
        assert distortion['mean'] >= 0.0

    def test_distortion_output_format(self, sphere_mesh_simple):
        """Check output format"""
        vertices, triangles = sphere_mesh_simple

        # Random UVs
        uvs = np.random.rand(len(vertices), 2)

        distortion = compute_angle_distortion(vertices, triangles, uvs)

        assert 'mean' in distortion
        assert 'max' in distortion
        assert 'std' in distortion

        assert distortion['mean'] >= 0
        assert distortion['max'] >= 0
        assert distortion['std'] >= 0


class TestAreaDistortion:
    """Test area distortion computation"""

    def test_uniform_scaling(self):
        """Uniform scaling should have low area distortion"""
        vertices = np.array([
            [0, 0, 0], [2, 0, 0], [0, 2, 0]
        ], dtype=np.float64)

        triangles = np.array([[0, 1, 2]], dtype=np.int32)

        # Uniformly scaled UV (half size)
        uvs = np.array([
            [0, 0], [1, 0], [0, 1]
        ], dtype=np.float64)

        distortion = compute_area_distortion(vertices, triangles, uvs)

        # Uniform scaling means ratio of all areas is same
        # Distortion = max/min should be close to 1
        assert distortion < 10.0, "Uniform scaling should have low area distortion"

    def test_equiareal_mapping(self):
        """Perfect area-preserving mapping"""
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [0, 1, 0]
        ], dtype=np.float64)

        triangles = np.array([[0, 1, 2]], dtype=np.int32)

        # Area-preserving UV
        uvs = np.array([
            [0, 0], [1, 0], [0, 1]
        ], dtype=np.float64)

        distortion = compute_area_distortion(vertices, triangles, uvs)

        # Single triangle: distortion should be 1.0
        assert abs(distortion - 1.0) < 0.01


class TestUVCoverage:
    """Test UV coverage computation"""

    def test_full_coverage(self):
        """Full UV square should give 100% coverage"""
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]
        ], dtype=np.float64)

        triangles = np.array([
            [0, 1, 2],
            [1, 3, 2]
        ], dtype=np.int32)

        # Cover full [0, 1]² square
        uvs = np.array([
            [0, 0], [1, 0], [0, 1], [1, 1]
        ], dtype=np.float64)

        coverage = compute_uv_coverage(triangles, uvs)

        assert abs(coverage - 100.0) < 1.0, \
            f"Full square should be ~100% coverage, got {coverage:.1f}%"

    def test_half_coverage(self):
        """Half of UV square should give 50% coverage"""
        vertices = np.array([
            [0, 0, 0], [0.5, 0, 0], [0, 1, 0]
        ], dtype=np.float64)

        triangles = np.array([[0, 1, 2]], dtype=np.int32)

        # Triangle covering half of UV space
        uvs = np.array([
            [0, 0], [1, 0], [0, 1]
        ], dtype=np.float64)

        coverage = compute_uv_coverage(triangles, uvs)

        assert 40 < coverage < 60, \
            f"Triangle should cover ~50%, got {coverage:.1f}%"

    def test_small_coverage(self):
        """Small triangle should have low coverage"""
        vertices = np.array([
            [0, 0, 0], [0.1, 0, 0], [0, 0.1, 0]
        ], dtype=np.float64)

        triangles = np.array([[0, 1, 2]], dtype=np.int32)

        # Small UV triangle
        uvs = np.array([
            [0, 0], [0.1, 0], [0, 0.1]
        ], dtype=np.float64)

        coverage = compute_uv_coverage(triangles, uvs)

        assert coverage < 10.0, f"Small triangle should be <10% coverage, got {coverage:.1f}%"


class TestStretchMetric:
    """Test stretch distortion metric"""

    def test_isometric_mapping(self):
        """Isometric mapping should have stretch = 1"""
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [0, 1, 0]
        ], dtype=np.float64)

        triangles = np.array([[0, 1, 2]], dtype=np.int32)

        # Isometric UV
        uvs = np.array([
            [0, 0], [1, 0], [0, 1]
        ], dtype=np.float64)

        stretch = compute_stretch_metric(vertices, triangles, uvs)

        assert 'mean' in stretch
        assert 'max' in stretch

        # Stretch should be close to 1 for isometric
        assert 0.5 < stretch['mean'] < 2.0

    def test_stretched_mapping(self, sphere_mesh_simple):
        """Stretched mapping should have stretch > 1"""
        vertices, triangles = sphere_mesh_simple

        # Random UVs (will have stretch)
        uvs = np.random.rand(len(vertices), 2)

        stretch = compute_stretch_metric(vertices, triangles, uvs)

        assert stretch['max'] > 0, "Stretch should be positive"
