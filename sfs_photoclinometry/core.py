"""Legacy compatibility wrappers for core SFS functions."""

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from lunardem.core.config import ReconstructionConfig
from lunardem.geometry.scaling import scale_dem_to_meters as _scale_dem_to_meters
from lunardem.methods.sfs import run_sfs_optimization as _run_sfs_optimization


def _legacy_to_config(config: Dict[str, Any]) -> ReconstructionConfig:
    return ReconstructionConfig.model_validate(
        {
            "illumination": {
                "sun_azimuth_deg": config.get("sun_azimuth_deg", 101.554510),
                "sun_elevation_deg": config.get("sun_elevation_deg", 34.802249),
            },
            "sensor": {
                "spacecraft_altitude_km": config.get("spacecraft_altitude_km", 95.85),
                "focal_length_mm": config.get("focal_length_mm", 140.0),
                "detector_pixel_width_um": config.get("detector_pixel_width_um", 7.0),
            },
            "sfs": {
                "regularization_lambda": config.get("regularization_lambda", 5e-3),
                "max_iterations": config.get("max_iterations", 150),
                "initial_surface": config.get("initial_surface", "flat"),
            },
        }
    )


def run_sfs_optimization(image: np.ndarray, config: Dict[str, Any]) -> np.ndarray:
    """Legacy wrapper for SFS optimization."""
    modern_config = _legacy_to_config(config)
    dem, _ = _run_sfs_optimization(image, modern_config)
    return dem


def scale_dem_to_meters(dem: np.ndarray, shape: tuple, config: Dict[str, Any]) -> np.ndarray:
    """Legacy wrapper for DEM scaling."""
    del shape
    modern_config = _legacy_to_config(config)
    return _scale_dem_to_meters(dem, modern_config.sensor)
