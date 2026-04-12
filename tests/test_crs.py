from __future__ import annotations

import numpy as np
import pytest

from lunadem.core.config import GeoreferenceConfig
from lunadem.io.raster import save_dem_as_geotiff

rasterio = pytest.importorskip("rasterio")


def test_geotiff_write_with_lunar_crs(tmp_path) -> None:
    dem = np.zeros((8, 8), dtype=np.float32)
    georef = GeoreferenceConfig()
    out = tmp_path / "dem.tif"
    path = save_dem_as_geotiff(out, dem, georef)
    assert out.exists()
    with rasterio.open(path) as src:
        assert src.crs is not None
