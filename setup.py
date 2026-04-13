"""Setuptools fallback configuration for lunadem.

Primary build configuration lives in `pyproject.toml`. This file is kept for
tooling compatibility and explicit metadata visibility.
"""

from pathlib import Path
import re

from setuptools import find_packages, setup


README = Path("README.md").read_text(encoding="utf-8")
VERSION_MATCH = re.search(
    r'^__version__ = ["\']([^"\']+)["\']',
    Path("lunadem/__init__.py").read_text(encoding="utf-8"),
    re.MULTILINE,
)
if VERSION_MATCH is None:
    raise RuntimeError("Unable to determine package version from lunadem/__init__.py")
VERSION = VERSION_MATCH.group(1)

setup(
    name="lunadem",
    version=VERSION,
    description="Production-ready DEM generation toolkit for lunar and planetary imagery.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="kartavya suryawanshi",
    author_email="kartavya.xenon@gmail.com",
    license="MIT",
    python_requires=">=3.9",
    packages=find_packages(exclude=("tests", "docs", "examples")),
    include_package_data=True,
    install_requires=[
        "numpy>=1.24,<2.1",
        "scipy>=1.10",
        "rasterio>=1.3",
        "imageio>=2.34",
        "imageio-ffmpeg>=0.5",
        "matplotlib>=3.8",
        "plotly>=5.22",
        "requests>=2.32",
        "pygame>=2.6",
        "pydantic>=2.8",
        "typer>=0.12",
        "PyYAML>=6.0",
        "onnxruntime>=1.18",
    ],
    extras_require={
        "ml": ["torch>=2.2", "onnx>=1.19", "ml-dtypes>=0.5", "scikit-learn>=1.5"],
        "viz": ["matplotlib>=3.8", "plotly>=5.22"],
        "pds": ["pvl>=1.3"],
        "native": ["pybind11>=2.12", "scikit-build-core>=0.10"],
        "docs": ["mkdocs>=1.6", "mkdocs-material>=9.5", "mkdocstrings[python]>=0.25"],
        "dev": [
            "pytest>=8.2",
            "pytest-cov>=5.0",
            "ruff>=0.6",
            "mypy>=1.10",
            "build>=1.2",
            "twine>=6.2",
            "wheel>=0.45",
            "types-PyYAML>=6.0",
            "onnx>=1.19",
            "ml-dtypes>=0.5",
            "scikit-learn>=1.5",
            "pybind11>=2.12",
            "scikit-build-core>=0.10",
        ],
        "release": ["build>=1.2", "twine>=6.2", "wheel>=0.45"],
    },
    package_data={
        "lunadem": [
            "assets/fun.mp3",
            "assets/noor.mp4",
            "assets/japneet.jpeg",
            "assets/docs/*.md",
            "assets/models/*.json",
            "assets/models/*.onnx",
        ],
        "lunardem": [
            "assets/fun.mp3",
            "assets/noor.mp4",
            "assets/japneet.jpeg",
        ],
    },
    entry_points={
        "console_scripts": [
            "lunadem=lunadem.cli:main",
            "lunardem=lunardem.cli:main",
            "creator=lunadem.cli:creator_main",
            "kartavya=lunadem.cli:kartavya_main",
            "babies=lunadem.cli:babies_main",
            "noor=lunadem.cli:noor_main",
            "overkill=lunadem.cli:overkill_main",
        ]
    },
    keywords=[
        "dem",
        "shape-from-shading",
        "photoclinometry",
        "lunar",
        "planetary",
        "geospatial",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: C++",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
)
