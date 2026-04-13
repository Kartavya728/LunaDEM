"""Rover-aware safe landing-site selection."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import numpy as np
import rasterio
from scipy.ndimage import binary_erosion, distance_transform_edt

from lunadem.core.config import AnalysisConfig, LandingConfig, ReconstructionConfig
from lunadem.core.models import LandingSiteResult, RoverSpec, TerrainMetrics
from lunadem.geometry.lighting import get_light_vector
from lunadem.geometry.surface import calculate_surface_normals
from lunadem.landing.analysis import compute_terrain_metrics
from lunadem.landing.rovers import get_rover_spec
from lunadem.landing.suitability import _hazard_map, assess_landing_suitability


def _disk(radius_px: int) -> np.ndarray:
    radius_px = max(int(radius_px), 1)
    yy, xx = np.ogrid[-radius_px : radius_px + 1, -radius_px : radius_px + 1]
    return (xx**2 + yy**2) <= radius_px**2


def _normalize(values: np.ndarray) -> np.ndarray:
    values = values.astype(np.float32)
    min_value = float(np.min(values))
    max_value = float(np.max(values))
    if max_value - min_value <= 1e-6:
        return np.zeros_like(values, dtype=np.float32)
    return (values - min_value) / (max_value - min_value)


def _load_surface(
    image_or_dem: np.ndarray | str | Path,
    *,
    method: str,
    reconstruct: bool | None,
    config: ReconstructionConfig | Mapping[str, Any] | None,
    analysis_config: AnalysisConfig | Mapping[str, Any] | None,
) -> tuple[np.ndarray, float, TerrainMetrics | None, bool]:
    from lunadem.core.api import analyze_dem, generate_dem

    internal_config = (
        config
        if config is not None
        else ReconstructionConfig(
            output={
                "output_dir": "output",
                "base_name": "landing_internal",
                "save_geotiff": False,
                "save_obj": False,
                "save_ply": False,
                "save_visualizations": False,
                "save_interactive_html": False,
                "save_manifest": False,
            }
        )
    )

    if isinstance(image_or_dem, np.ndarray):
        if reconstruct:
            result = generate_dem(image_or_dem, method=method, config=internal_config, analysis_config=analysis_config)
            return result.dem_meters, result.pixel_scale_m, result.metrics, True
        dem = image_or_dem.astype(np.float32)
        metrics = analyze_dem(dem, analysis_config=analysis_config)
        return dem, 1.0, metrics, False

    path = Path(image_or_dem)
    if not path.exists():
        raise FileNotFoundError(f"Surface input not found: {path}")

    if reconstruct is None:
        reconstruct = path.suffix.lower() not in {".tif", ".tiff"} or path.parent.name.lower() == "image"
        if "dem" in path.stem.lower() or "reconstructed" in path.stem.lower():
            reconstruct = False

    if reconstruct:
        result = generate_dem(path, method=method, config=internal_config, analysis_config=analysis_config)
        return result.dem_meters, result.pixel_scale_m, result.metrics, True

    with rasterio.open(path) as src:
        dem = src.read(1).astype(np.float32)
        pixel_size_m = float(abs(src.transform.a)) if src.transform else 1.0
    metrics = analyze_dem(dem, analysis_config=analysis_config)
    return dem, pixel_size_m, metrics, False


def _resolve_sun_vector(scene: Any = None, sun: Any = None) -> np.ndarray | None:
    if isinstance(sun, np.ndarray):
        norm = np.linalg.norm(sun)
        return None if norm <= 0 else sun / norm
    if isinstance(sun, Mapping):
        if "vector" in sun:
            vector = np.asarray(sun["vector"], dtype=np.float64)
            norm = np.linalg.norm(vector)
            return None if norm <= 0 else vector / norm
        if "sun_azimuth_deg" in sun and "sun_elevation_deg" in sun:
            return get_light_vector(float(sun["sun_azimuth_deg"]), float(sun["sun_elevation_deg"]))
    if scene is not None and getattr(scene, "geometry", None) is not None:
        return scene.geometry.sun_vector
    return None


def find_safe_landing_site(
    image_or_dem: np.ndarray | str | Path,
    *,
    rover: str | RoverSpec | Mapping[str, Any] | None = None,
    scene: Any = None,
    sun: Any = None,
    camera: Mapping[str, Any] | None = None,
    time: str | None = None,
    method: str = "hybrid",
    reconstruct: bool | None = None,
    config: ReconstructionConfig | Mapping[str, Any] | None = None,
    analysis_config: AnalysisConfig | Mapping[str, Any] | None = None,
    landing_config: LandingConfig | Mapping[str, Any] | None = None,
) -> LandingSiteResult:
    """Find the safest landing site for a rover on an image or DEM."""
    rover_spec = get_rover_spec(rover or "pragyan")
    dem, pixel_size_m, metrics, used_reconstruction = _load_surface(
        image_or_dem,
        method=method,
        reconstruct=reconstruct,
        config=config,
        analysis_config=analysis_config,
    )
    metrics = metrics or compute_terrain_metrics(dem, AnalysisConfig(pixel_size_m=pixel_size_m))

    if landing_config is None:
        resolved_landing_config = LandingConfig(pixel_size_m=pixel_size_m)
    elif isinstance(landing_config, Mapping):
        payload = dict(landing_config)
        payload.setdefault("pixel_size_m", pixel_size_m)
        resolved_landing_config = LandingConfig.model_validate(payload)
    else:
        resolved_landing_config = landing_config

    report = assess_landing_suitability(dem, resolved_landing_config, metrics=metrics)
    hazard_values = _hazard_map(dem, resolved_landing_config.constraints.hazard_window)

    footprint_radius_m = max(rover_spec.length_m, rover_spec.width_m) / 2.0 + rover_spec.safety_margin_m
    safe_radius_px = max(int(np.ceil(footprint_radius_m / max(pixel_size_m, 1e-6))), 1)
    footprint = _disk(safe_radius_px)

    clearance_mask = binary_erosion(report.safe_mask.astype(bool), structure=footprint, border_value=0)
    candidate_mask = clearance_mask if np.any(clearance_mask) else report.safe_mask.astype(bool)

    slope_score = 1.0 - np.clip(
        metrics.slope_deg / max(resolved_landing_config.constraints.max_slope_deg, 1e-6),
        0.0,
        1.0,
    )
    roughness_score = 1.0 - np.clip(
        metrics.roughness_m / max(resolved_landing_config.constraints.max_roughness_m, 1e-6),
        0.0,
        1.0,
    )
    hazard_score = 1.0 - np.clip(
        hazard_values / max(resolved_landing_config.constraints.hazard_height_m, 1e-6),
        0.0,
        1.0,
    )
    clearance_score = _normalize(distance_transform_edt(candidate_mask))

    score_map = 0.4 * slope_score + 0.25 * roughness_score + 0.2 * hazard_score + 0.15 * clearance_score
    sun_vector = _resolve_sun_vector(scene=scene, sun=sun)
    if sun_vector is not None:
        normals = calculate_surface_normals(dem)
        illumination = np.clip(np.sum(normals * sun_vector.reshape(1, 1, 3), axis=-1), 0.0, 1.0)
        score_map = 0.85 * score_map + 0.15 * illumination.astype(np.float32)

    masked_scores = np.where(candidate_mask, score_map, -np.inf)
    if not np.isfinite(masked_scores).any():
        masked_scores = score_map
    row, col = np.unravel_index(np.argmax(masked_scores), masked_scores.shape)
    best_score = float(masked_scores[row, col])
    x_m = float(col * pixel_size_m)
    y_m = float(row * pixel_size_m)

    summary = {
        "used_reconstruction": used_reconstruction,
        "method": method,
        "pixel_size_m": pixel_size_m,
        "footprint_radius_m": footprint_radius_m,
        "safe_radius_px": safe_radius_px,
        "time": time,
        "camera_metadata_available": camera is not None or scene is not None,
        "sun_vector": sun_vector.tolist() if sun_vector is not None else None,
        "safe_fraction": report.safe_fraction,
        "landing_score": report.score,
        "row": int(row),
        "col": int(col),
        "x_m": x_m,
        "y_m": y_m,
    }
    if scene is not None:
        summary["scene_id"] = getattr(scene, "scene_id", str(scene))

    return LandingSiteResult(
        row=int(row),
        col=int(col),
        score=best_score,
        pixel_size_m=float(pixel_size_m),
        x_m=x_m,
        y_m=y_m,
        safe_radius_px=safe_radius_px,
        rover=rover_spec,
        safe_mask=candidate_mask.astype(np.uint8),
        score_map=score_map.astype(np.float32),
        summary=summary,
        metrics=metrics,
        report=report,
    )
