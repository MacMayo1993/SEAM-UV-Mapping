"""
Setup script for non-orientable UV unwrapping package.
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="non-orientable-uv",
    version="1.0.0",
    author="MacMayo1993",
    description="Seamless UV unwrapping via non-orientable topology",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MacMayo1993/SEAM-UV-Mapping",
    packages=find_packages(exclude=["tests", "benchmarks", "docs", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-benchmark>=4.0.0",
            "black>=23.0.0",
            "ruff>=0.5.0",
            "mypy>=1.5.0",
            "matplotlib>=3.7.0",
        ],
        "mesh": [
            "trimesh>=3.23.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "non-orientable-benchmark=benchmarks.run_benchmarks:main",
        ],
    },
    include_package_data=True,
    package_data={
        "addon": ["shaders/*.glsl"],
    },
    keywords="uv-mapping mesh-parameterization topology blender computer-graphics",
    project_urls={
        "Bug Reports": "https://github.com/MacMayo1993/SEAM-UV-Mapping/issues",
        "Source": "https://github.com/MacMayo1993/SEAM-UV-Mapping",
        "Documentation": "https://github.com/MacMayo1993/SEAM-UV-Mapping/tree/main/docs",
    },
)
