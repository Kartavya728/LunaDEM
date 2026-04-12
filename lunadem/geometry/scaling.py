"""DEM scaling utilities."""

from __future__ import annotations

import numpy as np

from lunadem.core.config import SensorConfig


def pixel_scale_meters(sensor: SensorConfig) -> float:
    """Compute pixel ground sample distance in meters."""
    return (
        (sensor.detector_pixel_width_um * 1e-6)
        * (sensor.spacecraft_altitude_km * 1000.0)
        / (sensor.focal_length_mm * 1e-3)
    )


def scale_dem_to_meters(
    dem: np.ndarray,
    sensor: SensorConfig,
    center: bool = True,
) -> np.ndarray:
    """Scale relative DEM to metric units."""
    scaled = dem.astype(np.float32) * float(pixel_scale_meters(sensor))
    if center:
        scaled = scaled - float(np.mean(scaled))
    return scaled.astype(np.float32)
