from __future__ import annotations

import numpy as np

from lunadem.io.image import load_image


def test_load_image_normalized_range(synthetic_image_path) -> None:
    image, metadata = load_image(synthetic_image_path, normalize=True)
    assert image.dtype == np.float32
    assert image.min() >= 0.0
    assert image.max() <= 1.0
    assert "width" in metadata


def test_load_image_from_array(synthetic_image) -> None:
    image, metadata = load_image(synthetic_image, normalize=False)
    assert image.shape == synthetic_image.shape
    assert metadata["source"] == "in_memory"
