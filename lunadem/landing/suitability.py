"""Deterministic landing suitability scoring."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import label, maximum_filter, minimum_filter

from lunadem.core.config import LandingConfig
from lunadem.core.models import LandingReport, TerrainMetrics
from lunadem.landing.analysis import compute_terrain_metrics
from lunadem.native import native_hazard_map


def _hazard_map(dem: np.ndarray, window: int) -> np.ndarray:
    if native_hazard_map is not None:
        return np.asarray(native_hazard_map(dem.astype(np.float32), int(window)), dtype=np.float32)
    local_max = maximum_filter(dem, size=window, mode="nearest")
    local_min = minimum_filter(dem, size=window, mode="nearest")
    return (local_max - local_min).astype(np.float32)


def _filter_small_safe_regions(mask: np.ndarray, min_area: int) -> np.ndarray:
    labeled, n_components = label(mask)
    if n_components == 0:
        return mask.astype(bool)
    filtered = np.zeros_like(mask, dtype=bool)
    for component_id in range(1, n_components + 1):
        component = labeled == component_id
        if int(np.sum(component)) >= min_area:
            filtered |= component
    return filtered


def assess_landing_suitability(
    dem: np.ndarray,
    landing_config: LandingConfig,
    metrics: TerrainMetrics | None = None,
) -> LandingReport:
    """Evaluate safe landing regions based on slope, roughness, and hazards."""
    if metrics is None:
        from lunadem.core.config import AnalysisConfig

        metrics = compute_terrain_metrics(
            dem,
            AnalysisConfig(
                pixel_size_m=landing_config.pixel_size_m,
                roughness_window=5,
            ),
        )

    constraints = landing_config.constraints
    slope_mask = metrics.slope_deg <= constraints.max_slope_deg
    roughness_mask = metrics.roughness_m <= constraints.max_roughness_m
    hazard_map = _hazard_map(dem, constraints.hazard_window)
    hazard_mask = hazard_map <= constraints.hazard_height_m

    safe_mask = slope_mask & roughness_mask & hazard_mask
    safe_mask = _filter_small_safe_regions(
        safe_mask,
        constraints.min_safe_area_px,
    )

    safe_fraction = float(np.mean(safe_mask))
    score = float(
        100.0
        * (
            0.5 * safe_fraction
            + 0.25 * float(np.mean(slope_mask))
            + 0.25 * float(np.mean(roughness_mask))
        )
    )

    summary = {
        "safe_fraction": safe_fraction,
        "score": score,
        "max_slope_deg": constraints.max_slope_deg,
        "max_roughness_m": constraints.max_roughness_m,
        "hazard_height_m": constraints.hazard_height_m,
    }

    return LandingReport(
        safe_mask=safe_mask.astype(np.uint8),
        slope_mask=slope_mask.astype(np.uint8),
        roughness_mask=roughness_mask.astype(np.uint8),
        hazard_mask=hazard_mask.astype(np.uint8),
        safe_fraction=safe_fraction,
        score=score,
        summary=summary,
    )
