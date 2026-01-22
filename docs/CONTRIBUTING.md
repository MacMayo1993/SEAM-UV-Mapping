# Contributing to Non-Orientable UV Unwrapping

Thank you for your interest in contributing! This document provides guidelines and best practices.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing](#testing)
6. [Submitting Changes](#submitting-changes)
7. [Areas for Contribution](#areas-for-contribution)

## Code of Conduct

Be respectful, constructive, and collaborative. We're all here to learn and improve the project.

## Getting Started

### Prerequisites

- Python 3.10+
- Blender 3.6+ (for UI development)
- Git
- Basic understanding of differential geometry (helpful but not required)

### Setup Development Environment

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/SEAM-UV-Mapping.git
cd SEAM-UV-Mapping

# Add upstream remote
git remote add upstream https://github.com/MacMayo1993/SEAM-UV-Mapping.git

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Run tests to verify setup
pytest tests/ -v
```

## Development Workflow

### Branching Strategy

- `main`: Stable releases only
- `develop`: Active development
- `feature/your-feature`: New features
- `fix/issue-number`: Bug fixes

### Making Changes

```bash
# Update your fork
git checkout develop
git pull upstream develop

# Create feature branch
git checkout -b feature/my-new-feature

# Make your changes
# ... edit files ...

# Run tests
pytest tests/ -v

# Commit changes
git add .
git commit -m "feat: Add new feature description

- Detailed change 1
- Detailed change 2

Closes #123"

# Push to your fork
git push origin feature/my-new-feature

# Create Pull Request on GitHub
```

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic change)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(core): Add support for open surfaces

- Detect boundary edges
- Handle parity assignment at boundaries
- Update tests

Closes #42

---

fix(ui): Prevent crash on non-manifold meshes

Validates mesh topology before unwrapping.

Fixes #58

---

docs(readme): Update installation instructions

Added troubleshooting section for Windows users.
```

## Coding Standards

### Python Style

- **PEP 8** compliant
- Use `ruff` for linting: `ruff check .`
- Use `black` for formatting: `black .`
- Maximum line length: 100 characters

### Code Quality

```bash
# Format code
black addon/ tests/

# Lint code
ruff check addon/ tests/

# Type check
mypy addon/core/
```

### Documentation

- **Docstrings**: Google style
- **Type hints**: Required for all public functions
- **Comments**: Explain "why", not "what"

Example:

```python
def compute_gaussian_curvature(
    vertices: np.ndarray,
    triangles: np.ndarray
) -> np.ndarray:
    """
    Compute discrete Gaussian curvature at each vertex.

    Uses angle deficit method: K = 2π - Σ(angles at vertex).

    Args:
        vertices: (N, 3) array of vertex positions
        triangles: (M, 3) array of triangle indices

    Returns:
        (N,) array of Gaussian curvature values in radians

    Raises:
        ValueError: If mesh is non-manifold

    References:
        Meyer et al. "Discrete Differential-Geometry Operators" (2003)
    """
    # Implementation...
```

### Naming Conventions

- **Classes**: `PascalCase`
- **Functions**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: `_leading_underscore`

## Testing

### Writing Tests

- Place tests in `tests/test_<module>.py`
- Use pytest fixtures for common setup
- Aim for >80% code coverage

Example test:

```python
import pytest
import numpy as np
from addon.core.curvature import compute_gaussian_curvature

class TestCurvature:
    def test_sphere_positive_curvature(self, sphere_mesh):
        """Sphere should have positive curvature"""
        vertices, triangles = sphere_mesh
        K = compute_gaussian_curvature(vertices, triangles)

        assert np.all(K > 0), "Sphere has negative curvature"
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_curvature.py -v

# With coverage
pytest tests/ --cov=addon --cov-report=html

# Benchmarks
pytest tests/test_benchmarks.py --benchmark-only
```

### Test Requirements

- All new features must include tests
- Bug fixes must include regression tests
- Maintain or improve code coverage

## Submitting Changes

### Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] New features have tests
- [ ] Documentation updated (docstrings, README, etc.)
- [ ] Commit messages follow conventions
- [ ] No merge conflicts with `develop`

### Pull Request Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe tests added or run.

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
```

### Review Process

1. Automated CI checks must pass
2. At least one maintainer approval required
3. Address review feedback
4. Squash commits if requested
5. Maintainer merges PR

## Areas for Contribution

### High Priority

- **Support for non-manifold meshes**: Improve robustness
- **Alternative parameterizations**: LSCM, ABF++, etc.
- **Performance optimization**: GPU acceleration, parallelization
- **Documentation**: More tutorials and examples

### Good First Issues

Look for issues labeled `good-first-issue` or `help-wanted`:

- Adding unit tests
- Improving error messages
- Documentation improvements
- Code formatting fixes

### Research Contributions

- **Alternative edge scoring methods**: Beyond curvature jump
- **Adaptive k* selection**: Auto-tune threshold
- **High genus surfaces**: Improve quality for complex topology
- **Conformal/authalic variants**: Different optimization objectives

## Recognition

Contributors will be:
- Listed in `CONTRIBUTORS.md`
- Mentioned in release notes
- Acknowledged in academic papers (if applicable)

## Questions?

- Open a [Discussion](https://github.com/MacMayo1993/SEAM-UV-Mapping/discussions)
- Ask in an existing [Issue](https://github.com/MacMayo1993/SEAM-UV-Mapping/issues)
- Email: [maintainer-email]

Thank you for contributing! 🎉
