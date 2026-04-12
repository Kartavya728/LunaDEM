"""Raster export helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import rasterio
from rasterio.control import GroundControlPoint
from rasterio.transform import Affine, from_gcps

from lunadem.core.config import GeoreferenceConfig


def _transform_from_corner_coords(
    shape: tuple[int, int],
    georef: GeoreferenceConfig,
) -> Affine:
    if georef.corner_coords is None:
        return Affine.translation(0.0, 0.0) * Affine.scale(1.0, -1.0)

    height, width = shape
    corners = georef.corner_coords
    gcps = [
        GroundControlPoint(
            row=0,
            col=0,
            x=corners.upper_left.lon,
            y=corners.upper_left.lat,
        ),
        GroundControlPoint(
            row=0,
            col=width - 1,
            x=corners.upper_right.lon,
            y=corners.upper_right.lat,
        ),
        GroundControlPoint(
            row=height - 1,
            col=0,
            x=corners.lower_left.lon,
            y=corners.lower_left.lat,
        ),
        GroundControlPoint(
            row=height - 1,
            col=width - 1,
            x=corners.lower_right.lon,
            y=corners.lower_right.lat,
        ),
    ]
    return from_gcps(gcps)


def save_dem_as_geotiff(
    path: str | Path,
    dem: np.ndarray,
    georef: GeoreferenceConfig,
    metadata: Dict[str, Any] | None = None,
) -> str:
    """Save DEM as a compressed GeoTIFF."""
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    transform = _transform_from_corner_coords(dem.shape, georef)
    profile: Dict[str, Any] = {
        "driver": "GTiff",
        "height": int(dem.shape[0]),
        "width": int(dem.shape[1]),
        "count": 1,
        "dtype": str(dem.dtype),
        "crs": georef.crs,
        "transform": transform,
        "nodata": -9999.0,
        "compress": "lzw",
    }

    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(dem.astype(np.float32), 1)
        if metadata:
            dst.update_tags(**{k: str(v) for k, v in metadata.items()})
    return str(out_path)
