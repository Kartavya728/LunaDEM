"""Image loaders for scientific and standard image formats."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple

import imageio.v2 as imageio
import numpy as np
import rasterio

from lunardem.utils.arrays import normalize_to_unit_range


def _to_grayscale(img_raw: np.ndarray) -> np.ndarray:
    if img_raw.ndim == 2:
        return img_raw.astype(np.float32)
    if img_raw.ndim == 3 and img_raw.shape[2] >= 3:
        weights = np.array([0.299, 0.587, 0.114], dtype=np.float32)
        return np.dot(img_raw[..., :3], weights).astype(np.float32)
    if img_raw.ndim == 3:
        return img_raw[..., 0].astype(np.float32)
    raise ValueError(f"Unsupported image dimensions: {img_raw.shape}")


def _read_rasterio(path: Path) -> Tuple[np.ndarray, Dict[str, Any]]:
    with rasterio.open(path) as src:
        if src.count == 1:
            image = src.read(1).astype(np.float32)
        else:
            bands = src.read([1, 2, 3]).astype(np.float32)
            image = _to_grayscale(np.moveaxis(bands, 0, -1))
        metadata: Dict[str, Any] = {
            "width": src.width,
            "height": src.height,
            "dtype": str(src.dtypes[0]),
            "transform": tuple(src.transform),
            "crs": src.crs.to_string() if src.crs else None,
            "source_driver": src.driver,
        }
    return image, metadata


def load_image(
    image_input: str | Path | np.ndarray,
    normalize: bool = True,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Load PNG/JPG/TIFF/GeoTIFF or in-memory array.

    Returns
    -------
    tuple[np.ndarray, dict]
        `(image, metadata)` where image is float32 and metadata includes source details.
    """
    if isinstance(image_input, np.ndarray):
        image = _to_grayscale(image_input).astype(np.float32)
        metadata: Dict[str, Any] = {"source": "in_memory", "crs": None}
    else:
        path = Path(image_input)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")

        if path.suffix.lower() in {".tif", ".tiff"}:
            image, metadata = _read_rasterio(path)
        else:
            image_raw = imageio.imread(path)
            image = _to_grayscale(np.asarray(image_raw))
            metadata = {
                "source": str(path),
                "source_driver": "imageio",
                "crs": None,
                "width": int(image.shape[1]),
                "height": int(image.shape[0]),
            }

    if normalize:
        image = normalize_to_unit_range(image)
    return image.astype(np.float32), metadata
