from __future__ import annotations

from pathlib import Path

import imageio.v2 as imageio
import numpy as np
import pytest


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
