"""Typed result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import numpy as np


@dataclass
class TerrainMetrics:
    """Terrain analytics outputs."""

    slope_deg: np.ndarray
    roughness_m: np.ndarray
    curvature: np.ndarray
    stats: Dict[str, float]
    histograms: Dict[str, Any]


@dataclass
class LandingReport:
    """Landing suitability output and diagnostic maps."""

    safe_mask: np.ndarray
    slope_mask: np.ndarray
    roughness_mask: np.ndarray
    hazard_mask: np.ndarray
    safe_fraction: float
    score: float
    summary: Dict[str, Any]


@dataclass
class DEMResult:
    """DEM generation output."""

    dem_meters: np.ndarray
    method: str
    pixel_scale_m: float
    crs: str
    exports: Dict[str, Optional[str]] = field(default_factory=dict)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    metrics: Optional[TerrainMetrics] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
