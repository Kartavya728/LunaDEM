"""Terrain analytics derived from DEM."""

from __future__ import annotations

from typing import Dict

import numpy as np
from scipy.ndimage import laplace, uniform_filter

from lunardem.core.config import AnalysisConfig
from lunardem.core.models import TerrainMetrics


def _slope_deg(dem: np.ndarray, pixel_size_m: float) -> np.ndarray:
    dz_dy, dz_dx = np.gradient(dem, pixel_size_m)
    slope_rad = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
    return np.rad2deg(slope_rad).astype(np.float32)


def _roughness_std(dem: np.ndarray, window: int) -> np.ndarray:
    mean = uniform_filter(dem, size=window, mode="nearest")
    mean_sq = uniform_filter(dem**2, size=window, mode="nearest")
    variance = np.clip(mean_sq - mean**2, a_min=0.0, a_max=None)
    return np.sqrt(variance).astype(np.float32)


def _curvature_laplacian(dem: np.ndarray, pixel_size_m: float) -> np.ndarray:
    return (laplace(dem, mode="nearest") / (pixel_size_m**2)).astype(np.float32)


def _histogram(values: np.ndarray, bins: int) -> Dict[str, np.ndarray]:
    hist, edges = np.histogram(values, bins=bins)
    return {"counts": hist, "bin_edges": edges}


def compute_terrain_metrics(dem: np.ndarray, config: AnalysisConfig) -> TerrainMetrics:
    """Compute slope, roughness, curvature, and summary statistics."""
    slope = _slope_deg(dem, config.pixel_size_m)
    roughness = _roughness_std(dem, config.roughness_window)
    curvature = _curvature_laplacian(dem, config.pixel_size_m)

    stats = {
        "elevation_min_m": float(np.min(dem)),
        "elevation_max_m": float(np.max(dem)),
        "elevation_mean_m": float(np.mean(dem)),
        "slope_mean_deg": float(np.mean(slope)),
        "slope_p95_deg": float(np.percentile(slope, 95)),
        "roughness_mean_m": float(np.mean(roughness)),
        "roughness_p95_m": float(np.percentile(roughness, 95)),
        "curvature_mean": float(np.mean(curvature)),
    }

    histograms = {
        "elevation": _histogram(dem.ravel(), config.histogram_bins),
        "slope": _histogram(slope.ravel(), config.histogram_bins),
        "roughness": _histogram(roughness.ravel(), config.histogram_bins),
    }
    return TerrainMetrics(
        slope_deg=slope,
        roughness_m=roughness,
        curvature=curvature,
        stats=stats,
        histograms=histograms,
    )
