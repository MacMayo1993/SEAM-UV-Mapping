"""
Automated benchmark suite for comparing UV unwrapping methods.

This script runs comprehensive benchmarks on test meshes and generates
performance and quality metrics.
"""

import numpy as np
import time
import json
from pathlib import Path
from typing import Dict, Tuple, Optional

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not available, plots will not be generated")

# Import core algorithm
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from addon.core.topology import TopologicalUVAtlas
from addon.core.distortion import (
    compute_angle_distortion,
    compute_area_distortion,
    compute_uv_coverage
)


class BenchmarkRunner:
    """Run comprehensive benchmarks on test meshes"""

    def __init__(self, output_dir: Path = None):
        if output_dir is None:
            output_dir = Path(__file__).parent / "results"

        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = {}

    def generate_sphere_mesh(self, subdivisions: int = 2) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate icosphere mesh for testing.

        Args:
            subdivisions: Number of subdivisions (0-4)

        Returns:
            (vertices, triangles)
        """
        # Base icosahedron
        phi = (1 + np.sqrt(5)) / 2

        vertices = [
            [-1, phi, 0], [1, phi, 0], [-1, -phi, 0], [1, -phi, 0],
            [0, -1, phi], [0, 1, phi], [0, -1, -phi], [0, 1, -phi],
            [phi, 0, -1], [phi, 0, 1], [-phi, 0, -1], [-phi, 0, 1]
        ]

        triangles = [
            [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
            [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
            [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
            [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]
        ]

        vertices = np.array(vertices, dtype=np.float64)
        triangles = np.array(triangles, dtype=np.int32)

        # Subdivide
        for _ in range(subdivisions):
            vertices, triangles = self._subdivide_mesh(vertices, triangles)

        # Normalize to unit sphere
        vertices /= np.linalg.norm(vertices, axis=1, keepdims=True)

        return vertices, triangles

    def _subdivide_mesh(self, vertices: np.ndarray, triangles: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Subdivide mesh once (each triangle -> 4 triangles)"""
        edge_to_midpoint = {}
        new_vertices = list(vertices)

        def get_midpoint(v1: int, v2: int) -> int:
            edge = tuple(sorted([v1, v2]))
            if edge not in edge_to_midpoint:
                midpoint = (vertices[v1] + vertices[v2]) / 2.0
                edge_to_midpoint[edge] = len(new_vertices)
                new_vertices.append(midpoint)
            return edge_to_midpoint[edge]

        new_triangles = []
        for tri in triangles:
            v0, v1, v2 = tri

            # Get midpoints
            m01 = get_midpoint(v0, v1)
            m12 = get_midpoint(v1, v2)
            m20 = get_midpoint(v2, v0)

            # Create 4 new triangles
            new_triangles.append([v0, m01, m20])
            new_triangles.append([v1, m12, m01])
            new_triangles.append([v2, m20, m12])
            new_triangles.append([m01, m12, m20])

        return np.array(new_vertices, dtype=np.float64), np.array(new_triangles, dtype=np.int32)

    def benchmark_unwrap(
        self,
        name: str,
        vertices: np.ndarray,
        triangles: np.ndarray,
        k_star: float = 0.721
    ) -> Dict:
        """
        Run full benchmark on a mesh.

        Args:
            name: Benchmark name
            vertices: Vertex positions
            triangles: Triangle indices
            k_star: Stitch edge threshold

        Returns:
            Dictionary with benchmark results
        """
        print(f"\n{'='*60}")
        print(f"Benchmarking: {name}")
        print(f"{'='*60}")

        # Time unwrapping
        start = time.time()
        atlas = TopologicalUVAtlas(vertices, triangles, k_star=k_star, verbose=False)
        elapsed = time.time() - start

        # Compute metrics
        print("Computing distortion metrics...")
        angle_dist = compute_angle_distortion(vertices, triangles, atlas.vertex_uvs)
        area_dist = compute_area_distortion(vertices, triangles, atlas.vertex_uvs)
        coverage = compute_uv_coverage(triangles, atlas.vertex_uvs)

        results = {
            "mesh": name,
            "num_vertices": len(vertices),
            "num_triangles": len(triangles),
            "num_stitch_edges": len(atlas.stitch_edges),
            "k_star": k_star,
            "time_seconds": elapsed,
            "angle_distortion": {
                "mean_degrees": float(angle_dist['mean']),
                "max_degrees": float(angle_dist['max']),
                "std_degrees": float(angle_dist['std'])
            },
            "area_distortion": float(area_dist),
            "uv_coverage_percent": float(coverage),
        }

        print(f"\nResults:")
        print(f"  Time: {elapsed:.3f}s")
        print(f"  Stitch edges: {len(atlas.stitch_edges)} ({100*len(atlas.stitch_edges)/len(atlas.edges):.1f}%)")
        print(f"  Angle distortion: {angle_dist['mean']:.2f}° (mean), {angle_dist['max']:.2f}° (max)")
        print(f"  Area distortion: {area_dist:.2f}")
        print(f"  UV coverage: {coverage:.1f}%")

        return results

    def run_all_benchmarks(self):
        """Run benchmarks on generated test meshes"""
        print("\n" + "="*60)
        print("RUNNING BENCHMARK SUITE")
        print("="*60)

        # Generate test meshes
        test_cases = [
            ("sphere_low", 1),     # ~80 triangles
            ("sphere_med", 2),     # ~320 triangles
            ("sphere_high", 3),    # ~1280 triangles
        ]

        for mesh_name, subdivisions in test_cases:
            try:
                print(f"\nGenerating {mesh_name}...")
                vertices, triangles = self.generate_sphere_mesh(subdivisions)
                print(f"  {len(vertices)} vertices, {len(triangles)} triangles")

                results = self.benchmark_unwrap(mesh_name, vertices, triangles)
                self.results[mesh_name] = results

            except Exception as e:
                print(f"  ERROR: {e}")
                import traceback
                traceback.print_exc()

        # Save results
        output_file = self.output_dir / "benchmark_results.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n{'='*60}")
        print(f"Results saved to: {output_file}")
        print(f"{'='*60}\n")

    def compare_k_star_values(self):
        """Test sensitivity to k* parameter"""
        print("\n" + "="*60)
        print("K* SENSITIVITY ANALYSIS")
        print("="*60)

        vertices, triangles = self.generate_sphere_mesh(subdivisions=2)
        k_values = [0.50, 0.60, 0.65, 0.70, 0.721, 0.75, 0.80, 0.85, 0.90]

        results = []
        for k in k_values:
            print(f"\nTesting k* = {k:.3f}...")
            result = self.benchmark_unwrap(f"sphere_k{k:.3f}", vertices, triangles, k_star=k)
            results.append(result)

        # Save sensitivity results
        output_file = self.output_dir / "k_star_sensitivity.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        # Plot if matplotlib available
        if HAS_MATPLOTLIB:
            self._plot_k_star_sensitivity(results)

    def _plot_k_star_sensitivity(self, results: list):
        """Generate k* sensitivity plots"""
        k_values = [r['k_star'] for r in results]

        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # Angle distortion vs k*
        angles = [r['angle_distortion']['mean_degrees'] for r in results]
        axes[0, 0].plot(k_values, angles, 'o-', linewidth=2)
        axes[0, 0].axvline(0.721, color='r', linestyle='--', label='k*=0.721')
        axes[0, 0].set_xlabel('k* threshold')
        axes[0, 0].set_ylabel('Mean angle distortion (°)')
        axes[0, 0].legend()
        axes[0, 0].grid(True)

        # Coverage vs k*
        coverage = [r['uv_coverage_percent'] for r in results]
        axes[0, 1].plot(k_values, coverage, 'o-', linewidth=2)
        axes[0, 1].axvline(0.721, color='r', linestyle='--', label='k*=0.721')
        axes[0, 1].set_xlabel('k* threshold')
        axes[0, 1].set_ylabel('UV coverage (%)')
        axes[0, 1].legend()
        axes[0, 1].grid(True)

        # Num stitch edges vs k*
        stitches = [r['num_stitch_edges'] for r in results]
        axes[1, 0].plot(k_values, stitches, 'o-', linewidth=2)
        axes[1, 0].axvline(0.721, color='r', linestyle='--', label='k*=0.721')
        axes[1, 0].set_xlabel('k* threshold')
        axes[1, 0].set_ylabel('Number of stitch edges')
        axes[1, 0].legend()
        axes[1, 0].grid(True)

        # Time vs k*
        times = [r['time_seconds'] for r in results]
        axes[1, 1].plot(k_values, times, 'o-', linewidth=2)
        axes[1, 1].axvline(0.721, color='r', linestyle='--', label='k*=0.721')
        axes[1, 1].set_xlabel('k* threshold')
        axes[1, 1].set_ylabel('Time (seconds)')
        axes[1, 1].legend()
        axes[1, 1].grid(True)

        plt.tight_layout()
        plt.savefig(self.output_dir / "k_star_sensitivity.png", dpi=150)
        print(f"\nSensitivity plot saved to: {self.output_dir}/k_star_sensitivity.png")

    def plot_comparison(self):
        """Generate comparison plots"""
        if not self.results or not HAS_MATPLOTLIB:
            return

        meshes = list(self.results.keys())

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # Angle distortion comparison
        means = [self.results[m]['angle_distortion']['mean_degrees'] for m in meshes]
        axes[0].bar(meshes, means)
        axes[0].set_ylabel('Mean Angle Distortion (°)')
        axes[0].set_title('Angle Distortion')
        axes[0].tick_params(axis='x', rotation=45)

        # Coverage comparison
        coverage = [self.results[m]['uv_coverage_percent'] for m in meshes]
        axes[1].bar(meshes, coverage)
        axes[1].set_ylabel('UV Coverage (%)')
        axes[1].set_title('UV Space Utilization')
        axes[1].tick_params(axis='x', rotation=45)

        # Time comparison
        times = [self.results[m]['time_seconds'] for m in meshes]
        axes[2].bar(meshes, times)
        axes[2].set_ylabel('Time (seconds)')
        axes[2].set_title('Performance')
        axes[2].tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig(self.output_dir / "benchmark_comparison.png", dpi=150)
        print(f"Comparison plot saved to: {self.output_dir}/benchmark_comparison.png")


def main():
    """Run benchmark suite"""
    print("\n" + "="*60)
    print("NON-ORIENTABLE UV UNWRAPPING BENCHMARK SUITE")
    print("="*60)

    runner = BenchmarkRunner()

    # Run all benchmarks
    runner.run_all_benchmarks()

    # Test k* sensitivity
    runner.compare_k_star_values()

    # Generate comparison plots
    runner.plot_comparison()

    print("\n" + "="*60)
    print("BENCHMARK SUITE COMPLETE!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
