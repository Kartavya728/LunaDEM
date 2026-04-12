"""Legacy compatibility wrappers for IO helpers."""

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from lunadem.core.config import GeoreferenceConfig
from lunadem.io.image import load_image as _load_image
from lunadem.io.mesh import save_dem_as_obj as _save_dem_as_obj
from lunadem.io.raster import save_dem_as_geotiff as _save_dem_as_geotiff


def load_image(image_path: str) -> np.ndarray:
    image, _ = _load_image(image_path, normalize=True)
    return image


def _georef_from_legacy(config: Dict[str, Any]) -> GeoreferenceConfig:
    corners = config.get("refined_corner_coords")
    payload: Dict[str, Any] = {
        "crs": config.get("crs", "+proj=longlat +a=1737400 +b=1737400 +no_defs"),
        "projection": config.get("projection", "IAU_MOON"),
    }
    if corners:
        payload["corner_coords"] = corners
    return GeoreferenceConfig.model_validate(payload)


def save_dem_as_geotiff(save_path: str, dem: np.ndarray, shape: tuple, config: Dict[str, Any]) -> None:
    del shape
    georef = _georef_from_legacy(config)
    _save_dem_as_geotiff(save_path, dem, georef)


def save_dem_as_obj(save_path: str, dem: np.ndarray) -> None:
    _save_dem_as_obj(save_path, dem)
