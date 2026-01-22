"""
Basic UV unwrapping example using the standalone Python API.

This example demonstrates how to use the non-orientable UV unwrapping
algorithm without Blender.
"""

import sys
from pathlib import Path

import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from addon.core.distortion import (
    compute_angle_distortion,
    compute_area_distortion,
    compute_uv_coverage,
)
from addon.core.topology import TopologicalUVAtlas


def generate_icosphere(subdivisions: int = 2) -> tuple:
    """Generate icosphere mesh for testing"""
    phi = (1 + np.sqrt(5)) / 2

    vertices = np.array(
        [
            [-1, phi, 0],
            [1, phi, 0],
            [-1, -phi, 0],
            [1, -phi, 0],
            [0, -1, phi],
            [0, 1, phi],
            [0, -1, -phi],
            [0, 1, -phi],
            [phi, 0, -1],
            [phi, 0, 1],
            [-phi, 0, -1],
            [-phi, 0, 1],
        ],
        dtype=np.float64,
    )

    triangles = np.array(
        [
            [0, 11, 5],
            [0, 5, 1],
            [0, 1, 7],
            [0, 7, 10],
            [0, 10, 11],
            [1, 5, 9],
            [5, 11, 4],
            [11, 10, 2],
            [10, 7, 6],
            [7, 1, 8],
            [3, 9, 4],
            [3, 4, 2],
            [3, 2, 6],
            [3, 6, 8],
            [3, 8, 9],
            [4, 9, 5],
            [2, 4, 11],
            [6, 2, 10],
            [8, 6, 7],
            [9, 8, 1],
        ],
        dtype=np.int32,
    )

    # Normalize to unit sphere
    vertices /= np.linalg.norm(vertices, axis=1, keepdims=True)

    return vertices, triangles


def main():
    """Run basic unwrapping example"""
    print("=" * 60)
    print("Non-Orientable UV Unwrapping - Basic Example")
    print("=" * 60)

    # Generate test mesh
    print("\n1. Generating icosphere mesh...")
    vertices, triangles = generate_icosphere(subdivisions=2)
    print(f"   Mesh: {len(vertices)} vertices, {len(triangles)} triangles")

    # Run unwrapping
    print("\n2. Running non-orientable UV unwrapping...")
    atlas = TopologicalUVAtlas(vertices, triangles, k_star=0.721, verbose=True)

    # Get results
    print("\n3. Results:")
    stats = atlas.get_stats()
    print(f"   Vertices: {stats['num_vertices']}")
    print(f"   Triangles: {stats['num_triangles']}")
    print(f"   Edges: {stats['num_edges']}")
    print(f"   Stitch edges: {stats['num_stitch_edges']} ({stats['stitch_fraction'] * 100:.1f}%)")
    print(f"   k* threshold: {stats['k_star']}")

    # Compute distortion metrics
    print("\n4. Computing distortion metrics...")
    angle_dist = compute_angle_distortion(vertices, triangles, atlas.vertex_uvs)
    area_dist = compute_area_distortion(vertices, triangles, atlas.vertex_uvs)
    coverage = compute_uv_coverage(triangles, atlas.vertex_uvs)

    print("\n   Angle Distortion:")
    print(f"     Mean: {angle_dist['mean']:.2f}°")
    print(f"     Max:  {angle_dist['max']:.2f}°")
    print(f"     Std:  {angle_dist['std']:.2f}°")
    print(f"\n   Area Distortion: {area_dist:.2f}")
    print(f"   UV Coverage: {coverage:.1f}%")

    # Export results
    print("\n5. Exporting results...")
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    np.save(output_dir / "vertices.npy", vertices)
    np.save(output_dir / "triangles.npy", triangles)
    np.save(output_dir / "uvs.npy", atlas.vertex_uvs)
    np.save(output_dir / "parities.npy", atlas.vertex_parities)

    print(f"   Saved to: {output_dir}/")
    print("   - vertices.npy")
    print("   - triangles.npy")
    print("   - uvs.npy")
    print("   - parities.npy")

    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
