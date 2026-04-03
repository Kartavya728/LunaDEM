"""Validated configuration models."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field, PositiveFloat, ValidationInfo, field_validator


class IlluminationConfig(BaseModel):
    """Illumination geometry in degrees."""

    sun_azimuth_deg: float = Field(default=101.554510, ge=0.0, lt=360.0)
    sun_elevation_deg: float = Field(default=34.802249, gt=0.0, lt=90.0)


class SensorConfig(BaseModel):
    """Sensor/camera geometry used for DEM metric scaling."""

    spacecraft_altitude_km: PositiveFloat = 95.85
    focal_length_mm: PositiveFloat = 140.0
    detector_pixel_width_um: PositiveFloat = 7.0


class GeoPoint(BaseModel):
    """Simple planetary geographic point."""

    lat: float
    lon: float


class CornerCoordinates(BaseModel):
    """Four-corner georeferencing points."""

    upper_left: GeoPoint
    upper_right: GeoPoint
    lower_left: GeoPoint
    lower_right: GeoPoint


class GeoreferenceConfig(BaseModel):
    """Georeferencing metadata for planetary outputs."""

    crs: str = "+proj=longlat +a=1737400 +b=1737400 +no_defs"
    projection: str = "IAU_MOON"
    corner_coords: Optional[CornerCoordinates] = None


class PreprocessingConfig(BaseModel):
    """Image preprocessing controls."""

    normalize: bool = True
    gaussian_sigma: float = Field(default=0.0, ge=0.0, le=20.0)
    median_size: int = Field(default=0, ge=0, le=21)
    shadow_mask: bool = True
    shadow_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)

    @field_validator("median_size")
    @classmethod
    def validate_median_size(cls, value: int) -> int:
        if value not in (0, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21):
            raise ValueError("median_size must be 0 or an odd integer from 3 to 21.")
        return value


class SFSMethodConfig(BaseModel):
    """Classical shape-from-shading settings."""

    initial_surface: Literal["flat"] = "flat"
    regularization_lambda: float = Field(default=5e-3, gt=0.0, le=1.0)
    max_iterations: int = Field(default=150, ge=1, le=5000)
    convergence_tol: float = Field(default=1e-7, gt=0.0)
    multiscale_levels: int = Field(default=3, ge=1, le=8)
    downscale_factor: float = Field(default=0.5, gt=0.1, lt=1.0)


class MLMethodConfig(BaseModel):
    """ML DEM settings (plugin-ready baseline)."""

    enabled: bool = False
    model_path: Optional[str] = None
    fallback_smoothing_sigma: float = Field(default=1.2, ge=0.0, le=20.0)


class HybridMethodConfig(BaseModel):
    """Hybrid method settings."""

    blend_weight: float = Field(default=0.65, ge=0.0, le=1.0)
    fallback_to_sfs_on_ml_failure: bool = True


class OutputConfig(BaseModel):
    """File outputs and rendering controls."""

    output_dir: Path = Path("output")
    base_name: str = "reconstructed_dem"
    save_geotiff: bool = True
    save_obj: bool = True
    save_ply: bool = False
    save_visualizations: bool = True
    save_manifest: bool = True


class ReconstructionConfig(BaseModel):
    """Top-level reconstruction configuration."""

    illumination: IlluminationConfig = Field(default_factory=IlluminationConfig)
    sensor: SensorConfig = Field(default_factory=SensorConfig)
    georeference: GeoreferenceConfig = Field(default_factory=GeoreferenceConfig)
    preprocessing: PreprocessingConfig = Field(default_factory=PreprocessingConfig)
    sfs: SFSMethodConfig = Field(default_factory=SFSMethodConfig)
    ml: MLMethodConfig = Field(default_factory=MLMethodConfig)
    hybrid: HybridMethodConfig = Field(default_factory=HybridMethodConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnalysisConfig(BaseModel):
    """Terrain analytics configuration."""

    pixel_size_m: PositiveFloat = 1.0
    roughness_window: int = Field(default=5, ge=3, le=31)
    histogram_bins: int = Field(default=40, ge=8, le=200)

    @field_validator("roughness_window")
    @classmethod
    def validate_window(cls, value: int) -> int:
        if value % 2 == 0:
            raise ValueError("roughness_window must be odd.")
        return value


class LandingConstraints(BaseModel):
    """Vehicle constraints used for deterministic landing checks."""

    max_slope_deg: float = Field(default=12.0, ge=0.0, le=90.0)
    max_roughness_m: float = Field(default=1.5, ge=0.0)
    hazard_height_m: float = Field(default=0.8, ge=0.0)
    hazard_window: int = Field(default=5, ge=1, le=31)
    min_safe_area_px: int = Field(default=64, ge=1)

    @field_validator("hazard_window")
    @classmethod
    def validate_hazard_window(cls, value: int, info: ValidationInfo) -> int:
        if value % 2 == 0:
            raise ValueError("hazard_window must be odd.")
        return value


class LandingConfig(BaseModel):
    """Landing suitability configuration."""

    pixel_size_m: PositiveFloat = 1.0
    constraints: LandingConstraints = Field(default_factory=LandingConstraints)
