"""Typed result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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


@dataclass
class SceneGeometry:
    """Derived scene geometry and acquisition metadata."""

    acquisition_duration_s: Optional[float] = None
    line_time_s: Optional[float] = None
    centroid_lat_deg: Optional[float] = None
    centroid_lon_deg: Optional[float] = None
    bbox_deg: Optional[Tuple[float, float, float, float]] = None
    bbox_area_deg2: Optional[float] = None
    bbox_area_km2: Optional[float] = None
    gsd_m: Optional[float] = None
    image_shape: Optional[Tuple[int, int]] = None
    ground_width_m: Optional[float] = None
    ground_height_m: Optional[float] = None
    ground_area_km2: Optional[float] = None
    transform: Optional[Tuple[float, ...]] = None
    sun_vector: Optional[np.ndarray] = None
    mean_camera_position_km: Optional[np.ndarray] = None
    mean_camera_velocity_km_s: Optional[np.ndarray] = None
    mean_camera_distance_km: Optional[float] = None
    mean_sun_position_km: Optional[np.ndarray] = None
    mean_sun_distance_km: Optional[float] = None
    camera_path_length_km: Optional[float] = None
    view_azimuth_deg: Optional[float] = None
    off_nadir_deg: Optional[float] = None
    footprint_lonlat: List[Tuple[float, float]] = field(default_factory=list)
    footprint_xyz_m: List[Tuple[float, float, float]] = field(default_factory=list)


@dataclass
class KaguyaScene:
    """Loaded Kaguya scene with typed metadata."""

    scene_id: str
    scene_dir: Path
    item_path: Path
    camera_path: Path
    image_path: Path
    thumbnail_path: Optional[Path]
    stac_item: Dict[str, Any]
    camera_model: Dict[str, Any]
    geometry: SceneGeometry


@dataclass
class MetadataPrediction:
    """Aggregated metadata prediction result."""

    model_name: str
    targets: Dict[str, float]
    uncertainty: Dict[str, float]
    metrics: Dict[str, float]
    patch_count: int
    source: str


@dataclass
class RoverSpec:
    """Rover footprint and visualization parameters."""

    name: str
    length_m: float
    width_m: float
    height_m: float
    ground_clearance_m: float = 0.2
    safety_margin_m: float = 0.25
    source: str = ""
    mesh_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LandingSiteResult:
    """Best landing site for a rover on an image or DEM."""

    row: int
    col: int
    score: float
    pixel_size_m: float
    x_m: float
    y_m: float
    safe_radius_px: int
    rover: RoverSpec
    safe_mask: np.ndarray
    score_map: np.ndarray
    summary: Dict[str, Any] = field(default_factory=dict)
    metrics: Optional[TerrainMetrics] = None
    report: Optional[LandingReport] = None
