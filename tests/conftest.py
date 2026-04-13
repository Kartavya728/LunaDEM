from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path

import imageio.v2 as imageio
import matplotlib
import numpy as np
import pytest
from _pytest import pathlib as pytest_pathlib
from _pytest import tmpdir as pytest_tmpdir

os.environ.setdefault("MPLBACKEND", "Agg")
matplotlib.use("Agg")

_ORIGINAL_CLEANUP_DEAD_SYMLINKS = pytest_pathlib.cleanup_dead_symlinks


def _safe_cleanup_dead_symlinks(root: Path) -> None:
    try:
        _ORIGINAL_CLEANUP_DEAD_SYMLINKS(root)
    except PermissionError:
        return


pytest_pathlib.cleanup_dead_symlinks = _safe_cleanup_dead_symlinks
pytest_tmpdir.cleanup_dead_symlinks = _safe_cleanup_dead_symlinks


def pytest_configure(config) -> None:
    config.option.basetemp = str(Path.cwd() / f"pytest-work-base-{os.getpid()}")


@pytest.fixture()
def tmp_path() -> Path:
    root = Path.cwd() / "pytest-generated"
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"lunadem-test-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


@pytest.fixture()
def synthetic_image() -> np.ndarray:
    x = np.linspace(0, 1, 32, dtype=np.float32)
    y = np.linspace(0, 1, 32, dtype=np.float32)
    xx, yy = np.meshgrid(x, y)
    image = 0.5 * np.sin(2 * np.pi * xx) + 0.5 * yy
    image = image - image.min()
    image = image / max(image.max(), 1e-6)
    return image.astype(np.float32)


@pytest.fixture()
def synthetic_image_path(tmp_path: Path, synthetic_image: np.ndarray) -> Path:
    path = tmp_path / "synthetic.png"
    imageio.imwrite(path, (synthetic_image * 255).astype(np.uint8))
    return path
