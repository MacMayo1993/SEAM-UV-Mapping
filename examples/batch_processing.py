"""
Batch processing example: unwrap multiple meshes.

This example demonstrates how to unwrap multiple meshes in batch
and compare results.
"""

import numpy as np
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from addon.core.topology import TopologicalUVAtlas
from addon.core.distortion import compute_angle_distortion, compute_uv_coverage


def generate_test_meshes() -> dict:
    """Generate several test meshes"""
    meshes = {}

    # Sphere (low res)
    phi = (1 + np.sqrt(5)) / 2
    vertices = np.array([
        [-1, phi, 0], [1, phi, 0], [-1, -phi, 0], [1, -phi, 0],
        [0, -1, phi], [0, 1, phi], [0, -1, -phi], [0, 1, -phi],
        [phi, 0, -1], [phi, 0, 1], [-phi, 0, -1], [-phi, 0, 1]
    ], dtype=np.float64)
    vertices /= np.linalg.norm(vertices, axis=1, keepdims=True)

    triangles = np.array([
        [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
        [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
        [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
        [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]
    ], dtype=np.int32)

    meshes["sphere"] = (vertices, triangles)

    # Cube
    vertices = np.array([
        [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
        [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
    ], dtype=np.float64)

    triangles = np.array([
        [0, 1, 2], [0, 2, 3],  # Front
        [4, 6, 5], [4, 7, 6],  # Back
        [0, 4, 5], [0, 5, 1],  # Bottom
        [2, 6, 7], [2, 7, 3],  # Top
        [0, 3, 7], [0, 7, 4],  # Left
        [1, 5, 6], [1, 6, 2],  # Right
    ], dtype=np.int32)

    meshes["cube"] = (vertices, triangles)

    return meshes


def unwrap_mesh(name: str, vertices: np.ndarray, triangles: np.ndarray, k_star: float = 0.721) -> dict:
    """Unwrap a single mesh and return metrics"""
    print(f"\nProcessing: {name}")
    print(f"  {len(vertices)} vertices, {len(triangles)} triangles")

    # Unwrap
    atlas = TopologicalUVAtlas(vertices, triangles, k_star=k_star, verbose=False)

    # Compute metrics
    angle_dist = compute_angle_distortion(vertices, triangles, atlas.vertex_uvs)
    coverage = compute_uv_coverage(triangles, atlas.vertex_uvs)

    results = {
        "name": name,
        "num_vertices": len(vertices),
        "num_triangles": len(triangles),
        "num_stitch_edges": len(atlas.stitch_edges),
        "angle_distortion_mean": float(angle_dist['mean']),
        "angle_distortion_max": float(angle_dist['max']),
        "uv_coverage": float(coverage),
    }

    print(f"  Stitch edges: {len(atlas.stitch_edges)}")
    print(f"  Angle distortion: {angle_dist['mean']:.2f}° (mean)")
    print(f"  UV coverage: {coverage:.1f}%")

    return results


def main():
    """Run batch processing"""
    print("="*60)
    print("Batch Processing Example")
    print("="*60)

    # Generate meshes
    print("\nGenerating test meshes...")
    meshes = generate_test_meshes()

    # Process each mesh
    results = []
    for name, (vertices, triangles) in meshes.items():
        result = unwrap_mesh(name, vertices, triangles)
        results.append(result)

    # Save results
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "batch_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Results saved to: {output_file}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
