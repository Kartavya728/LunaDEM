from __future__ import annotations

import numpy as np

from lunadem.core.config import SensorConfig
from lunadem.geometry.scaling import pixel_scale_meters, scale_dem_to_meters


def test_pixel_scale_positive() -> None:
    sensor = SensorConfig(
        spacecraft_altitude_km=100.0,
        focal_length_mm=140.0,
        detector_pixel_width_um=7.0,
    )
    assert pixel_scale_meters(sensor) > 0


def test_scaled_dem_centered() -> None:
    sensor = SensorConfig()
    dem = np.array([[0.0, 1.0], [2.0, 3.0]], dtype=np.float32)
    scaled = scale_dem_to_meters(dem, sensor, center=True)
    assert np.isclose(np.mean(scaled), 0.0, atol=1e-5)
