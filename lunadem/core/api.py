"""Top-level public API for lunadem."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import rasterio

from lunadem.core.config import AnalysisConfig, LandingConfig, ReconstructionConfig
from lunadem.core.models import DEMResult, LandingReport, TerrainMetrics
from lunadem.core.registry import MethodRegistry
from lunadem.geometry.scaling import pixel_scale_meters, scale_dem_to_meters
from lunadem.io.image import load_image
from lunadem.io.manifest import save_manifest
from lunadem.io.mesh import save_dem_as_obj, save_dem_as_ply
from lunadem.io.raster import save_dem_as_geotiff
from lunadem.landing.analysis import compute_terrain_metrics
from lunadem.landing.suitability import assess_landing_suitability
from lunadem.methods import register_default_methods
from lunadem.utils.files import ensure_directory
from lunadem.utils.logging import get_logger

LOGGER = get_logger(__name__)

_REGISTRY = MethodRegistry()
register_default_methods(_REGISTRY)


def _as_reconstruction_config(config: ReconstructionConfig | Dict[str, Any] | None) -> ReconstructionConfig:
    if config is None:
        return ReconstructionConfig()
    if isinstance(config, ReconstructionConfig):
        return config
    return ReconstructionConfig.model_validate(config)


def _as_analysis_config(
    config: AnalysisConfig | Dict[str, Any] | None,
    pixel_size_m: float,
) -> AnalysisConfig:
    if config is None:
        return AnalysisConfig(pixel_size_m=pixel_size_m)
    if isinstance(config, AnalysisConfig):
        return config
    data = dict(config)
    data.setdefault("pixel_size_m", pixel_size_m)
    return AnalysisConfig.model_validate(data)


def _as_landing_config(
    config: LandingConfig | Dict[str, Any] | None,
    pixel_size_m: float,
) -> LandingConfig:
    if config is None:
        return LandingConfig(pixel_size_m=pixel_size_m)
    if isinstance(config, LandingConfig):
        return config
    data = dict(config)
    data.setdefault("pixel_size_m", pixel_size_m)
    return LandingConfig.model_validate(data)


def _load_dem_from_input(dem_or_path: np.ndarray | str | Path) -> tuple[np.ndarray, float]:
    if isinstance(dem_or_path, np.ndarray):
        return dem_or_path.astype(np.float32), 1.0

    path = Path(dem_or_path)
    if not path.exists():
        raise FileNotFoundError(f"DEM not found: {path}")
    if path.suffix.lower() in {".tif", ".tiff"}:
        with rasterio.open(path) as src:
            dem = src.read(1).astype(np.float32)
            pixel_size = float(abs(src.transform.a)) if src.transform else 1.0
            return dem, pixel_size
    image, _ = load_image(path, normalize=False)
    return image.astype(np.float32), 1.0


def _save_exports(
    dem_meters: np.ndarray,
    config: ReconstructionConfig,
    diagnostics: Dict[str, Any],
    metrics: TerrainMetrics,
    source_metadata: Dict[str, Any],
    method: str,
) -> Dict[str, Optional[str]]:
    output_dir = ensure_directory(config.output.output_dir)
    base = output_dir / config.output.base_name

    exports: Dict[str, Optional[str]] = {
        "geotiff": None,
        "obj": None,
        "ply": None,
        "depth_map_png": None,
        "surface_3d_png": None,
        "surface_3d_html": None,
        "manifest_json": None,
    }

    if config.output.save_geotiff:
        exports["geotiff"] = save_dem_as_geotiff(
            path=base.with_suffix(".tif"),
            dem=dem_meters,
            georef=config.georeference,
            metadata={
                "method": method,
                "projection": config.georeference.projection,
                **source_metadata,
                **config.metadata,
            },
        )
    if config.output.save_obj:
        exports["obj"] = save_dem_as_obj(base.with_suffix(".obj"), dem_meters)
    if config.output.save_ply:
        exports["ply"] = save_dem_as_ply(base.with_suffix(".ply"), dem_meters)

    if config.output.save_visualizations:
        try:
            from lunadem.visualization import plot_3d_surface_interactive
            from lunadem.visualization.plots import plot_3d_surface, plot_depth_map

            depth_map_path = base.with_name("depth_map.png")
            surface_png_path = base.with_name("surface_3d.png")
            plot_depth_map(dem_meters, depth_map_path, show=False)
            plot_3d_surface(dem_meters, surface_png_path, show=False)
            exports["depth_map_png"] = str(depth_map_path)
            exports["surface_3d_png"] = str(surface_png_path)
            if config.output.save_interactive_html:
                html_path = base.with_name("surface_3d.html")
                plot_3d_surface_interactive(dem_meters, title="Interactive Reconstructed Surface", save_path=html_path, show=False)
                exports["surface_3d_html"] = str(html_path)
        except Exception as exc:
            LOGGER.warning("Visualization export skipped: %s", exc)

    if config.output.save_manifest:
        histogram_summary = {
            key: {
                "counts": metrics.histograms[key]["counts"].tolist(),
                "bin_edges": metrics.histograms[key]["bin_edges"].tolist(),
            }
            for key in metrics.histograms
        }
        manifest_payload = {
            "method": method,
            "config": config.model_dump(mode="json"),
            "diagnostics": diagnostics,
            "metrics": {
                "stats": metrics.stats,
                "histograms": histogram_summary,
            },
            "exports": exports,
        }
        exports["manifest_json"] = save_manifest(
            base.with_name(f"{config.output.base_name}_manifest.json"),
            manifest_payload,
        )
    return exports


def generate_dem(
    input_data: np.ndarray | str | Path,
    method: str = "sfs",
    config: ReconstructionConfig | Dict[str, Any] | None = None,
    analysis_config: AnalysisConfig | Dict[str, Any] | None = None,
) -> DEMResult:
    """Generate a DEM from image input.

    Parameters
    ----------
    input_data:
        Input image array or path to image file.
    method:
        Reconstruction method name (`sfs`, `multiscale_sfs`, `ml`, `hybrid`).
    config:
        Reconstruction configuration model or dictionary.
    analysis_config:
        Terrain-analysis configuration model or dictionary.
    """
    cfg = _as_reconstruction_config(config)
    image, source_metadata = load_image(input_data, normalize=False)

    method_impl = _REGISTRY.get(method)
    method_result = method_impl.run(image=image, config=cfg)

    scaled_dem = scale_dem_to_meters(method_result.dem, cfg.sensor)
    px_scale = float(pixel_scale_meters(cfg.sensor))
    metrics_cfg = _as_analysis_config(analysis_config, pixel_size_m=px_scale)
    metrics = compute_terrain_metrics(scaled_dem, metrics_cfg)

    exports = _save_exports(
        dem_meters=scaled_dem,
        config=cfg,
        diagnostics=method_result.diagnostics,
        metrics=metrics,
        source_metadata=source_metadata,
        method=method,
    )

    metadata = {"source": source_metadata, **cfg.metadata}
    return DEMResult(
        dem_meters=scaled_dem,
        method=method,
        pixel_scale_m=px_scale,
        crs=cfg.georeference.crs,
        exports=exports,
        diagnostics=method_result.diagnostics,
        metrics=metrics,
        metadata=metadata,
    )


def analyze_dem(
    dem_or_path: np.ndarray | str | Path,
    analysis_config: AnalysisConfig | Dict[str, Any] | None = None,
) -> TerrainMetrics:
    """Analyze an existing DEM."""
    dem, pixel_size = _load_dem_from_input(dem_or_path)
    cfg = _as_analysis_config(analysis_config, pixel_size_m=pixel_size)
    return compute_terrain_metrics(dem, cfg)


def assess_landing(
    dem_or_path: np.ndarray | str | Path,
    landing_config: LandingConfig | Dict[str, Any] | None = None,
    analysis_config: AnalysisConfig | Dict[str, Any] | None = None,
) -> LandingReport:
    """Assess landing suitability for a DEM."""
    dem, pixel_size = _load_dem_from_input(dem_or_path)
    metrics = analyze_dem(dem, analysis_config=analysis_config)
    config = _as_landing_config(landing_config, pixel_size_m=pixel_size)
    return assess_landing_suitability(dem=dem, landing_config=config, metrics=metrics)
