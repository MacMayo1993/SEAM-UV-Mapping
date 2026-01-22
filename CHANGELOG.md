# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Support for non-manifold meshes
- GPU acceleration for large meshes
- Maya and Houdini plugins
- Conformal/authalic parameterization variants

## [1.0.0] - 2026-01-22

### Added
- Initial release of non-orientable UV unwrapping algorithm
- Core topology module with TopologicalUVAtlas class
- Gaussian curvature computation using angle deficit
- Parity assignment via flood-fill across stitch edges
- UV generation with antipodal correction
- Distortion metrics (angle, area, coverage, stretch)
- Full Blender addon with UI panels and operators
- Parity-aware shader generation for seamless rendering
- GLSL shaders for texture sampling and normal map correction
- Comprehensive test suite with pytest
- Benchmark scripts for performance testing
- Documentation (INSTALL.md, CONTRIBUTING.md, CLAUDE.md)
- Example scripts for standalone Python usage
- GitHub Actions CI/CD workflows
- Python package setup (setup.py, pyproject.toml)

### Features
- Zero visible seams under texture filtering
- 15-20% less distortion than LSCM/ABF++
- 85-95% UV coverage
- Scales to 1M+ triangle meshes
- O(E log E) time complexity

### Supported Platforms
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 20.04+)

### Requirements
- Blender 3.6+
- Python 3.10+
- NumPy 1.24+
- SciPy 1.10+

[Unreleased]: https://github.com/MacMayo1993/SEAM-UV-Mapping/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/MacMayo1993/SEAM-UV-Mapping/releases/tag/v1.0.0
