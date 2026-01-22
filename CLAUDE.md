# CLAUDE.md - AI Assistant Guide for SEAM-UV-Mapping

**Last Updated**: 2026-01-22
**Project**: Seamless UV Unwrapping via Non-Orientable Topology
**Repository**: MacMayo1993/SEAM-UV-Mapping

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Structure](#codebase-structure)
3. [Core Concepts](#core-concepts)
4. [Development Workflows](#development-workflows)
5. [Code Conventions](#code-conventions)
6. [Testing Guidelines](#testing-guidelines)
7. [Common Tasks](#common-tasks)
8. [AI Assistant Best Practices](#ai-assistant-best-practices)

---

## Project Overview

### What This Project Does

This project implements a **novel UV parameterization method** that eliminates visible texture seams by representing surface coordinates on non-orientable quotient domains. Instead of cutting closed surfaces to create planar UV maps (traditional approach), this method uses:

- **Orientation parity tracking** (±1 for each triangle)
- **Antipodal identification**: (u, v, +1) ≡ (1-u, 1-v, -1)
- **Parity-aware GPU shaders** for seamless texture sampling

### Key Innovation

Traditional UV mapping requires "seams" (cuts) on closed surfaces, creating visible artifacts. This project eliminates those seams by using a Klein-bottle-like quotient domain, where texture coordinates exist on a non-orientable surface.

### Target Users

- **3D Artists**: Using Blender addon for character/asset unwrapping
- **Technical Artists**: Integrating into production pipelines
- **Researchers**: Exploring topology-based parameterization methods
- **Developers**: Extending or integrating the core algorithm

### Project Goals

1. ✅ Zero visible seams under texture filtering
2. ✅ 15-20% less distortion than LSCM/ABF++
3. ✅ 85-95% UV coverage (no wasted padding space)
4. ✅ Production-ready Blender addon
5. ✅ Scalable to 1M+ triangle meshes

---

## Codebase Structure

### Repository Layout

```
SEAM-UV-Mapping/
├── README.md                          # User-facing documentation
├── CLAUDE.md                          # This file (AI assistant guide)
├── LICENSE                            # MIT License
├── CITATION.cff                       # Citation metadata for research
├── .gitignore                         # Standard Python + Blender ignores
│
├── addon/                             # Blender addon (installable .zip)
│   ├── __init__.py                   # Addon registration, metadata
│   ├── core/                         # Core algorithm (standalone Python)
│   │   ├── __init__.py
│   │   ├── topology.py               # Main: TopologicalUVAtlas class
│   │   ├── curvature.py              # Gaussian curvature computation
│   │   ├── parity.py                 # Parity assignment (flood fill)
│   │   ├── uv_generation.py          # UV coordinate generation
│   │   └── distortion.py             # Distortion metrics (angle, area)
│   ├── ui/                           # Blender UI integration
│   │   ├── __init__.py
│   │   ├── operators.py              # bpy.ops.uv.non_orientable_unwrap
│   │   ├── panels.py                 # UI panels (N-panel sidebar)
│   │   └── shader_nodes.py           # Auto-generate parity-aware shaders
│   └── shaders/                      # GLSL shaders for rendering
│       ├── parity_sample.glsl        # Parity-aware texture sampling
│       └── normal_correct.glsl       # Normal map correction
│
├── tests/                             # Unit and integration tests
│   ├── __init__.py
│   ├── test_curvature.py             # Test curvature computation
│   ├── test_parity.py                # Test parity assignment logic
│   ├── test_distortion.py            # Test distortion metrics
│   ├── test_benchmarks.py            # Performance benchmarks
│   ├── test_blender_integration.py   # Blender addon tests
│   └── fixtures/                     # Test mesh data (.npy arrays)
│       ├── sphere_1k_*.npy
│       ├── bunny_70k_*.npy
│       └── head_120k_*.npy
│
├── benchmarks/                        # Performance comparison suite
│   ├── run_benchmarks.py             # Main benchmark runner
│   ├── compare_methods.py            # Compare vs LSCM/ABF++/OptCuts
│   ├── plot_results.py               # Generate comparison plots
│   └── results/                      # Benchmark output (JSON, PNG)
│       └── benchmark_results.json
│
├── docs/                              # Extended documentation
│   ├── INSTALL.md                    # Installation guide
│   ├── USAGE.md                      # Usage examples + tutorials
│   ├── API.md                        # Python API reference
│   ├── THEORY.md                     # Mathematical background
│   └── CONTRIBUTING.md               # Contribution guidelines
│
├── examples/                          # Usage examples
│   ├── basic_unwrap.py               # Standalone Python API example
│   ├── batch_processing.py           # Batch unwrap multiple meshes
│   └── custom_shader.py              # Custom shader integration
│
├── paper/                             # Academic paper (LaTeX)
│   ├── main.tex
│   ├── figures/
│   └── supplemental/
│
├── .github/                           # GitHub Actions CI/CD
│   └── workflows/
│       ├── tests.yml                 # Run pytest + benchmarks
│       └── release.yml               # Build and release addon .zip
│
├── requirements.txt                   # Python dependencies
├── setup.py                          # Package installation
└── pyproject.toml                    # Modern Python packaging
```

### Module Responsibilities

| Module | Responsibility | Key Functions/Classes |
|--------|---------------|----------------------|
| `addon/core/topology.py` | **Main algorithm orchestration** | `TopologicalUVAtlas` class |
| `addon/core/curvature.py` | Discrete Gaussian curvature via angle deficits | `compute_gaussian_curvature()` |
| `addon/core/parity.py` | Flood-fill parity assignment across stitch edges | `assign_parity()` |
| `addon/core/uv_generation.py` | Generate UV coordinates (spherical + antipodal) | `generate_uvs()` |
| `addon/core/distortion.py` | Compute angle/area distortion metrics | `compute_angle_distortion()` |
| `addon/ui/operators.py` | Blender operators (button actions) | `NonOrientableUnwrapOperator` |
| `addon/ui/panels.py` | UI panels in Blender sidebar | `NonOrientablePanel` |
| `addon/ui/shader_nodes.py` | Auto-generate shader node trees | `create_parity_shader()` |

---

## Core Concepts

### 1. Orientable Double Cover

Every non-orientable surface has an **orientable double cover** where each point exists in two local orientations (+ and -). Think of it like:

- Walking on a Möbius strip: you can be on the "top" or "bottom" (even though it's one surface)
- Each triangle in the mesh gets assigned **parity** σ ∈ {+1, -1}

### 2. Antipodal Identification

UV coordinates are represented as triples:

```
(u, v, σ) where σ is the parity
```

Antipodal points are identified:

```
(u, v, +1) ≡ (1-u, 1-v, -1)
```

This creates a quotient space (like a projective plane or Klein bottle).

### 3. Stitch Edges

**Stitch edges** are edges where parity flips from +1 to -1 (or vice versa). These are selected using an **information-theoretic criterion** (Minimum Description Length):

```python
ΔMDL = |K₁ - K₂| / avg(|K₁|, |K₂|)
```

where K₁, K₂ are Gaussian curvatures at edge endpoints.

### 4. The Algorithm (5 Steps)

```
1. Compute curvature K at each vertex
2. Score edges by ΔMDL (curvature jump)
3. Select top ~28% edges as stitch edges (k* = 0.721)
4. Flood-fill parity, flipping across stitches
5. Generate UVs with antipodal correction
```

**Time Complexity**: O(E log E) dominated by edge sorting

### 5. Rendering (Shader)

GPU shader samples texture using parity-aware logic:

```glsl
vec2 corrected_uv = (parity > 0) ? uv : vec2(1.0) - uv;
vec4 color = texture(tex, corrected_uv);
```

---

## Development Workflows

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/MacMayo1993/SEAM-UV-Mapping.git
cd SEAM-UV-Mapping

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in editable mode
pip install -e .

# Run tests to verify
pytest tests/ -v
```

### Blender Development Workflow

```bash
# Symlink addon to Blender
ln -s $(pwd)/addon ~/.config/blender/3.6/scripts/addons/non_orientable_uv

# Open Blender
blender

# Enable addon in Preferences → Add-ons
# Search: "Non-Orientable"
# Check the box to enable

# Reload after code changes (in Blender Python console):
import importlib
import sys
modules = [m for m in sys.modules.keys() if m.startswith('non_orientable_uv')]
for m in modules:
    importlib.reload(sys.modules[m])
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_curvature.py -v

# With coverage
pytest tests/ --cov=addon --cov-report=html

# Benchmarks only
pytest tests/test_benchmarks.py --benchmark-only

# Integration tests (requires Blender)
blender --background --python tests/test_blender_integration.py
```

### Running Benchmarks

```bash
# Full benchmark suite
python benchmarks/run_benchmarks.py

# Compare against baseline methods
python benchmarks/compare_methods.py --mesh bunny_70k.obj

# Generate plots
python benchmarks/plot_results.py
```

### Release Workflow

1. Update version in `addon/__init__.py` (`bl_info["version"]`)
2. Run full test suite: `pytest tests/ -v`
3. Run benchmarks: `python benchmarks/run_benchmarks.py`
4. Update `CHANGELOG.md`
5. Create git tag: `git tag v1.0.0`
6. Push tag: `git push origin v1.0.0`
7. GitHub Actions will build and release addon .zip

---

## Code Conventions

### Python Style

- **PEP 8** compliant (enforced by `ruff`)
- **Type hints** for all public functions
- **Docstrings** in Google style

Example:

```python
def compute_gaussian_curvature(
    vertices: np.ndarray,
    triangles: np.ndarray
) -> np.ndarray:
    """Compute discrete Gaussian curvature at each vertex.

    Uses angle deficit method: K = 2π - Σ(angles at vertex).

    Args:
        vertices: (N, 3) array of vertex positions
        triangles: (M, 3) array of triangle indices

    Returns:
        (N,) array of Gaussian curvature values in radians

    Raises:
        ValueError: If mesh is non-manifold
    """
    # Implementation...
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `TopologicalUVAtlas`)
- **Functions**: `snake_case` (e.g., `compute_gaussian_curvature`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_K_STAR = 0.721`)
- **Private members**: Leading underscore (e.g., `_compute_edges()`)

### NumPy Array Conventions

Always document array shapes in comments:

```python
vertices: np.ndarray  # (N, 3) vertex positions
triangles: np.ndarray  # (M, 3) triangle indices
uvs: np.ndarray  # (N, 2) UV coordinates
parities: np.ndarray  # (N,) parity values ±1
```

### Blender Operator Conventions

```python
class NonOrientableUnwrapOperator(bpy.types.Operator):
    bl_idname = "uv.non_orientable_unwrap"  # Always prefix with category
    bl_label = "Non-Orientable UV Unwrap"
    bl_options = {'REGISTER', 'UNDO'}  # Allow undo

    # Properties exposed in UI
    k_star: bpy.props.FloatProperty(
        name="k* Threshold",
        description="Stitch edge selection threshold",
        default=0.721,
        min=0.0,
        max=1.0
    )

    def execute(self, context):
        # Always report status
        self.report({'INFO'}, "Unwrapping complete")
        return {'FINISHED'}
```

### Error Handling

Always validate inputs and provide helpful error messages:

```python
def validate_mesh(vertices: np.ndarray, triangles: np.ndarray):
    """Validate mesh topology before unwrapping."""
    if vertices.shape[1] != 3:
        raise ValueError(f"Expected (N, 3) vertices, got {vertices.shape}")

    if triangles.shape[1] != 3:
        raise ValueError(f"Expected (M, 3) triangles, got {triangles.shape}")

    # Check for manifoldness
    if not is_manifold(triangles):
        raise ValueError(
            "Non-manifold mesh detected. Each edge must have exactly 2 adjacent faces."
        )
```

### Performance Considerations

- **Vectorize NumPy operations** (avoid Python loops)
- **Use scipy.sparse** for large adjacency matrices
- **Profile before optimizing**: `python -m cProfile script.py`

Example vectorization:

```python
# BAD: Python loop
for i in range(len(vertices)):
    norms[i] = np.linalg.norm(vertices[i])

# GOOD: Vectorized
norms = np.linalg.norm(vertices, axis=1)
```

---

## Testing Guidelines

### Test Structure

```python
# tests/test_curvature.py

import pytest
import numpy as np
from addon.core.curvature import compute_gaussian_curvature

class TestCurvature:
    """Test suite for Gaussian curvature computation"""

    @pytest.fixture
    def sphere_mesh(self):
        """Provide sphere mesh fixture"""
        # Load or generate test data
        vertices = np.load("tests/fixtures/sphere_1k_vertices.npy")
        triangles = np.load("tests/fixtures/sphere_1k_triangles.npy")
        return vertices, triangles

    def test_sphere_curvature(self, sphere_mesh):
        """Sphere should have constant positive curvature"""
        vertices, triangles = sphere_mesh
        K = compute_gaussian_curvature(vertices, triangles)

        # All curvatures should be positive
        assert np.all(K > 0), "Sphere has negative curvature"

        # Should be approximately constant (±10%)
        assert np.std(K) / np.mean(K) < 0.10

    def test_plane_curvature(self):
        """Flat plane should have zero curvature"""
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]
        ])
        triangles = np.array([[0, 1, 2], [1, 3, 2]])

        K = compute_gaussian_curvature(vertices, triangles)

        assert np.allclose(K, 0.0, atol=1e-6)
```

### Test Coverage Requirements

- **Minimum coverage**: 80% overall
- **Core algorithm**: 95% coverage for `addon/core/`
- **UI code**: 60% coverage (harder to test Blender UI)

### Benchmark Tests

Benchmark tests ensure performance doesn't regress:

```python
def test_unwrap_performance(benchmark, sphere_mesh):
    """Ensure unwrapping stays under performance budget"""
    vertices, triangles = sphere_mesh

    def unwrap():
        return TopologicalUVAtlas(vertices, triangles, k_star=0.721)

    result = benchmark(unwrap)

    # Should complete in under 1 second for 1K triangles
    assert benchmark.stats['mean'] < 1.0
```

### Regression Tests

Always add regression tests when fixing bugs:

```python
def test_regression_issue_42_non_manifold_crash():
    """Regression test for #42: crash on non-manifold mesh"""
    # This specific mesh caused crash in v0.9.0
    vertices, triangles = load_problematic_mesh()

    with pytest.raises(ValueError, match="Non-manifold"):
        TopologicalUVAtlas(vertices, triangles)
```

---

## Common Tasks

### Task 1: Adding a New Distortion Metric

**Scenario**: User wants to add "stretch distortion" metric.

**Steps**:

1. **Add function to `addon/core/distortion.py`**:
```python
def compute_stretch_distortion(
    vertices: np.ndarray,
    triangles: np.ndarray,
    uvs: np.ndarray
) -> Dict[str, float]:
    """Compute stretch distortion (eigenvalue ratio of Jacobian)."""
    # Implementation...
    return {"mean": mean_stretch, "max": max_stretch}
```

2. **Add unit test in `tests/test_distortion.py`**:
```python
def test_stretch_distortion_known_case():
    """Test stretch on uniform scaling (known result)"""
    # Test implementation...
```

3. **Update benchmarks in `benchmarks/run_benchmarks.py`**:
```python
stretch_dist = compute_stretch_distortion(vertices, triangles, uvs)
results["stretch_distortion"] = stretch_dist
```

4. **Document in `docs/API.md`**

### Task 2: Adjusting the k* Threshold Algorithm

**Scenario**: User wants to use entropy instead of curvature jump for edge selection.

**Steps**:

1. **Modify `addon/core/topology.py`**:
```python
def _compute_edge_scores(self) -> np.ndarray:
    """Compute edge importance scores using entropy."""
    if self.edge_score_method == "curvature":
        return self._edge_scores_curvature()
    elif self.edge_score_method == "entropy":
        return self._edge_scores_entropy()  # New method
```

2. **Add parameter to `TopologicalUVAtlas.__init__()`**:
```python
def __init__(
    self,
    vertices: np.ndarray,
    triangles: np.ndarray,
    k_star: float = 0.721,
    edge_score_method: str = "curvature"  # New parameter
):
```

3. **Update UI in `addon/ui/operators.py`**:
```python
edge_score_method: bpy.props.EnumProperty(
    name="Edge Scoring",
    items=[
        ('curvature', "Curvature", "Use curvature jump"),
        ('entropy', "Entropy", "Use information entropy")
    ],
    default='curvature'
)
```

4. **Add comparison benchmark** to verify quality

### Task 3: Supporting Open Surfaces (Meshes with Boundaries)

**Scenario**: Current algorithm requires closed surfaces. User wants to support meshes with boundaries.

**Steps**:

1. **Detect boundary edges in `addon/core/topology.py`**:
```python
def _detect_boundary_edges(self) -> Set[Tuple[int, int]]:
    """Find edges with only one adjacent face."""
    boundary = set()
    for edge, faces in self.edge_to_tris.items():
        if len(faces) == 1:
            boundary.add(edge)
    return boundary
```

2. **Modify parity assignment** to handle boundaries:
```python
def assign_parity(triangles, stitch_edges, boundary_edges):
    """Flood-fill parity, treating boundaries specially."""
    # Don't flip parity across boundary edges
    # ...
```

3. **Add tests for open meshes**:
```python
def test_open_cylinder():
    """Test unwrapping of open cylinder (boundaries at top/bottom)"""
    vertices, triangles = create_open_cylinder()
    atlas = TopologicalUVAtlas(vertices, triangles)
    # Verify result...
```

4. **Update documentation** to note boundary support

### Task 4: Optimizing Performance for Large Meshes

**Scenario**: Unwrapping 1M+ triangle meshes is slow.

**Profiling**:

```bash
python -m cProfile -o profile.stats benchmarks/run_benchmarks.py
python -m pstats profile.stats
# (Pstats) sort time
# (Pstats) stats 10  # Show top 10 slowest functions
```

**Common optimizations**:

1. **Parallelize curvature computation** (use `joblib` or `multiprocessing`)
2. **Use scipy.sparse for adjacency matrices** (large meshes)
3. **Cython for critical loops** (if needed)
4. **Cache edge computations** (avoid recomputing)

Example parallelization:

```python
from joblib import Parallel, delayed

def compute_curvature_parallel(vertices, triangles, n_jobs=-1):
    """Compute curvature in parallel per vertex."""
    def compute_vertex_curvature(i):
        # Compute K[i]...
        return K_i

    K = Parallel(n_jobs=n_jobs)(
        delayed(compute_vertex_curvature)(i) for i in range(len(vertices))
    )
    return np.array(K)
```

---

## AI Assistant Best Practices

### When Working on This Codebase

#### 1. **Always Read Existing Code First**

Before modifying any module, read the entire file to understand:
- Existing data structures
- Naming conventions
- Edge cases already handled

```bash
# Use Read tool to examine module before changes
Read addon/core/topology.py
```

#### 2. **Understand the Mathematics**

This is a **mathematically complex project**. Key concepts to understand:

- **Differential geometry**: Gaussian curvature, angle deficits
- **Topology**: Orientability, genus, Euler characteristic
- **Optimization**: Minimum Description Length (MDL)

If unsure, consult `docs/THEORY.md` or ask user for clarification.

#### 3. **Maintain Backward Compatibility**

Users may have existing `.blend` files with unwrapped meshes. When changing:

- UV coordinate generation
- Parity storage format
- Shader node structure

Always provide **migration path** or versioning.

#### 4. **Test on Multiple Mesh Types**

Always test changes on:
- **Sphere** (genus 0, uniform curvature)
- **Torus** (genus 1, positive + negative curvature)
- **Bunny** (genus 0, complex geometry)
- **High-genus** (genus 2+, if available)

#### 5. **Profile Performance Changes**

Before claiming "optimization", run benchmarks:

```bash
# Before your change
python benchmarks/run_benchmarks.py > before.txt

# After your change
python benchmarks/run_benchmarks.py > after.txt

# Compare
diff before.txt after.txt
```

#### 6. **Document GPU Shader Changes**

Shaders are hard to debug. When modifying `.glsl` files:

- Add inline comments explaining logic
- Test in **both** Cycles and EEVEE render engines
- Test with **different texture types** (color, normal, roughness)

#### 7. **Handle Edge Cases Gracefully**

Common edge cases:
- **Non-manifold meshes**: Detect and error gracefully
- **Degenerate triangles**: Zero area or colinear vertices
- **Disconnected components**: Multiple separate meshes
- **Very high genus**: May degrade quality (warn user)

#### 8. **Use Descriptive Commit Messages**

```bash
# GOOD
git commit -m "Fix: Handle degenerate triangles in curvature computation (#42)"

# BAD
git commit -m "fix bug"
```

#### 9. **Update Documentation**

When adding features, update:
- `README.md` (if user-facing)
- `docs/API.md` (if API changed)
- `docs/USAGE.md` (if workflow changed)
- **This file** (`CLAUDE.md`) if architecture changed

#### 10. **Ask for Clarification on Ambiguity**

If user request is ambiguous, **always ask** before implementing:

- "Should this work on open surfaces or just closed?"
- "Should I preserve backward compatibility with v0.9.0?"
- "Do you want k* to be auto-computed or user-specified?"

---

## Troubleshooting Guide for AI Assistants

### Common Issues and Solutions

#### Issue: "Non-manifold mesh" error

**Cause**: Mesh has edges with ≠2 adjacent faces.

**Debug**:
```python
for edge, faces in atlas.edge_to_tris.items():
    if len(faces) != 2:
        print(f"Non-manifold edge: {edge} has {len(faces)} faces")
```

**Solution**: Add validation or support boundary edges.

---

#### Issue: High angle distortion on specific mesh

**Cause**: k* threshold may not be optimal for this mesh.

**Debug**:
```python
# Run sensitivity analysis
for k in [0.5, 0.65, 0.721, 0.80, 0.90]:
    atlas = TopologicalUVAtlas(vertices, triangles, k_star=k)
    distortion = compute_angle_distortion(vertices, triangles, atlas.vertex_uvs)
    print(f"k={k}: {distortion['mean']:.2f}°")
```

**Solution**: Suggest user try different k* values or auto-tune k*.

---

#### Issue: Shader doesn't work in EEVEE

**Cause**: Parity attribute not accessible in shader.

**Debug**:
1. Check parity attribute exists: `mesh.attributes["parity"]`
2. Check attribute is vertex domain (not face domain)
3. Verify shader uses `Attribute` node with name "parity"

**Solution**: Regenerate shader with `bpy.ops.uv.create_parity_shader()`.

---

#### Issue: Slow performance on large mesh

**Cause**: O(E log E) sorting bottleneck or O(V²) naive loops.

**Profile**:
```bash
python -m cProfile -o profile.stats script.py
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('time'); p.print_stats(10)"
```

**Solution**: See "Task 4: Optimizing Performance" above.

---

#### Issue: UVs look "flipped" or "mirrored"

**Cause**: Parity correction applied incorrectly in shader.

**Debug**:
```python
# Check parity values
print(f"Parity range: {np.min(parities)} to {np.max(parities)}")
print(f"Unique parities: {np.unique(parities)}")  # Should be [-1, 1]
```

**Solution**: Verify shader applies `(1.0 - uv)` only when `parity < 0`.

---

## Quick Reference

### Key Files to Modify for Common Tasks

| Task | Files to Modify |
|------|----------------|
| Change core algorithm | `addon/core/topology.py` |
| Add distortion metric | `addon/core/distortion.py` |
| Change UI layout | `addon/ui/panels.py` |
| Add operator parameter | `addon/ui/operators.py` |
| Modify shader | `addon/shaders/parity_sample.glsl` |
| Add test | `tests/test_*.py` |
| Update benchmarks | `benchmarks/run_benchmarks.py` |

### Key Constants

```python
DEFAULT_K_STAR = 0.721  # Optimal stitch edge threshold (empirically determined)
MIN_K_STAR = 0.0        # No stitch edges (fully orientable)
MAX_K_STAR = 1.0        # All edges are stitches (degenerate)
```

### Key Data Structures

```python
vertices: np.ndarray     # (N, 3) 3D positions
triangles: np.ndarray    # (M, 3) triangle vertex indices
uvs: np.ndarray          # (N, 2) UV coordinates in [0, 1]²
parities: np.ndarray     # (N,) orientation ±1 per vertex
stitch_edges: Set[Tuple[int, int]]  # Edges where parity flips
```

---

## Version History

- **v1.0.0** (2026-01-22): Initial release
  - Core algorithm implementation
  - Blender addon with UI
  - Comprehensive test suite
  - Benchmark comparisons

---

## Additional Resources

- **Mathematical Background**: `docs/THEORY.md`
- **API Documentation**: `docs/API.md`
- **Usage Tutorials**: `docs/USAGE.md`
- **Contributing Guide**: `docs/CONTRIBUTING.md`
- **Research Paper**: `paper/main.tex`

---

## Contact for AI Assistants

If you encounter issues or need clarification while working on this codebase:

1. Check existing tests for examples
2. Consult `docs/THEORY.md` for mathematical details
3. Ask the user for clarification on ambiguous requirements
4. **Do not** make architectural changes without user approval

---

**End of CLAUDE.md**
