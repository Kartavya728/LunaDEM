"""Setuptools fallback configuration for LunarDEM.

Primary build configuration lives in `pyproject.toml`. This file is kept for
tooling compatibility and explicit metadata visibility.
"""

from pathlib import Path

from setuptools import find_packages, setup


README = Path("README.md").read_text(encoding="utf-8")

setup(
    name="lunadem",
    version="0.1.0",
    description="Production-ready DEM generation toolkit for lunar and planetary imagery.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="kartavya suryawanshi",
    author_email="kartavya.xenon@gmail.com",
    license="MIT",
    python_requires=">=3.9,<3.13",
    packages=find_packages(exclude=("tests", "docs", "examples")),
    include_package_data=True,
    install_requires=[
        "numpy>=1.24",
        "scipy>=1.10",
        "rasterio>=1.3",
        "imageio>=2.34",
        "pydantic>=2.8",
        "typer>=0.12",
        "PyYAML>=6.0",
    ],
    extras_require={
        "ml": ["torch>=2.2"],
        "viz": ["matplotlib>=3.8"],
        "pds": ["pvl>=1.3"],
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
        ],
        "release": ["build>=1.2", "twine>=6.2", "wheel>=0.45"],
    },
    entry_points={"console_scripts": ["lunardem=lunardem.cli:main"]},
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
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
)
