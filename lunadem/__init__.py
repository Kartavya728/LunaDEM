"""lunadem public package API with lazy exports."""

from __future__ import annotations

from importlib import import_module

__version__ = "0.4.0"

_EXPORT_MAP = {
    "AnalysisConfig": ("lunadem.core.config", "AnalysisConfig"),
    "DEFAULT_MOON_CRS": ("lunadem.geometry.planetary", "DEFAULT_MOON_CRS"),
    "DEMResult": ("lunadem.core.models", "DEMResult"),
    "GeoreferenceConfig": ("lunadem.core.config", "GeoreferenceConfig"),
    "HybridMethodConfig": ("lunadem.core.config", "HybridMethodConfig"),
    "IlluminationConfig": ("lunadem.core.config", "IlluminationConfig"),
    "KaguyaScene": ("lunadem.core.models", "KaguyaScene"),
    "LandingConfig": ("lunadem.core.config", "LandingConfig"),
    "LandingConstraints": ("lunadem.core.config", "LandingConstraints"),
    "LandingReport": ("lunadem.core.models", "LandingReport"),
    "LandingSiteResult": ("lunadem.core.models", "LandingSiteResult"),
    "MLMethodConfig": ("lunadem.core.config", "MLMethodConfig"),
    "MOON_RADIUS_M": ("lunadem.geometry.planetary", "MOON_RADIUS_M"),
    "MetadataPrediction": ("lunadem.core.models", "MetadataPrediction"),
    "OutputConfig": ("lunadem.core.config", "OutputConfig"),
    "PreprocessingConfig": ("lunadem.core.config", "PreprocessingConfig"),
    "ReconstructionConfig": ("lunadem.core.config", "ReconstructionConfig"),
    "RoverSpec": ("lunadem.core.models", "RoverSpec"),
    "SFSMethodConfig": ("lunadem.core.config", "SFSMethodConfig"),
    "SceneGeometry": ("lunadem.core.models", "SceneGeometry"),
    "SensorConfig": ("lunadem.core.config", "SensorConfig"),
    "TEST_SCENE_ID": ("lunadem.datasets", "TEST_SCENE_ID"),
    "TerrainMetrics": ("lunadem.core.models", "TerrainMetrics"),
    "acquisition_duration_seconds": ("lunadem.geometry.conversions", "acquisition_duration_seconds"),
    "analyze_dem": ("lunadem.core.api", "analyze_dem"),
    "assess_landing": ("lunadem.core.api", "assess_landing"),
    "bbox_area_deg2": ("lunadem.geometry.conversions", "bbox_area_deg2"),
    "bbox_area_km2": ("lunadem.geometry.conversions", "bbox_area_km2"),
    "build_scene_summary": ("lunadem.datasets", "build_scene_summary"),
    "calculate_predicted_image": ("lunadem.geometry.surface", "calculate_predicted_image"),
    "calculate_surface_normals": ("lunadem.geometry.surface", "calculate_surface_normals"),
    "cartesian_to_latlon_moon": ("lunadem.geometry.conversions", "cartesian_to_latlon_moon"),
    "deg_to_rad": ("lunadem.geometry.conversions", "deg_to_rad"),
    "download_test_scene": ("lunadem.datasets", "download_test_scene"),
    "ensure_directory": ("lunadem.utils.files", "ensure_directory"),
    "extract_pds_geometry": ("lunadem.io.pds", "extract_pds_geometry"),
    "find_safe_landing_site": ("lunadem.landing", "find_safe_landing_site"),
    "get_scene_bbox": ("lunadem.datasets", "get_scene_bbox"),
    "get_scene_camera_summary": ("lunadem.datasets", "get_scene_camera_summary"),
    "get_scene_centroid": ("lunadem.datasets", "get_scene_centroid"),
    "get_scene_footprint_lonlat": ("lunadem.datasets", "get_scene_footprint_lonlat"),
    "get_scene_footprint_xyz": ("lunadem.datasets", "get_scene_footprint_xyz"),
    "get_scene_ground_area_km2": ("lunadem.datasets", "get_scene_ground_area_km2"),
    "get_scene_ground_coverage": ("lunadem.datasets", "get_scene_ground_coverage"),
    "get_scene_sun_summary": ("lunadem.datasets", "get_scene_sun_summary"),
    "get_scene_sun_vector": ("lunadem.datasets", "get_scene_sun_vector"),
    "get_scene_time_range": ("lunadem.datasets", "get_scene_time_range"),
    "get_scene_transform": ("lunadem.datasets", "get_scene_transform"),
    "get_scene_view_angles": ("lunadem.datasets", "get_scene_view_angles"),
    "generate_dem": ("lunadem.core.api", "generate_dem"),
    "get_light_vector": ("lunadem.geometry.lighting", "get_light_vector"),
    "get_model_artifact_paths": ("lunadem.ml", "get_model_artifact_paths"),
    "get_model_metrics": ("lunadem.ml", "get_model_metrics"),
    "get_model_targets": ("lunadem.ml", "get_model_targets"),
    "get_rover_spec": ("lunadem.landing", "get_rover_spec"),
    "get_sfs_assumptions": ("lunadem.sfs_theory", "get_sfs_assumptions"),
    "get_sfs_math": ("lunadem.sfs_theory", "get_sfs_math"),
    "get_sfs_terms": ("lunadem.sfs_theory", "get_sfs_terms"),
    "get_test_scene_manifest": ("lunadem.datasets", "get_test_scene_manifest"),
    "ground_coverage_meters": ("lunadem.geometry.conversions", "ground_coverage_meters"),
    "km_to_m": ("lunadem.geometry.conversions", "km_to_m"),
    "latlon_to_cartesian_moon": ("lunadem.geometry.conversions", "latlon_to_cartesian_moon"),
    "line_time_seconds": ("lunadem.geometry.conversions", "line_time_seconds"),
    "list_model_names": ("lunadem.ml", "list_model_names"),
    "list_available_rovers": ("lunadem.landing", "list_available_rovers"),
    "list_kaguya_scenes": ("lunadem.datasets", "list_kaguya_scenes"),
    "load_camera_model": ("lunadem.datasets", "load_camera_model"),
    "load_image": ("lunadem.io.image", "load_image"),
    "load_kaguya_scene": ("lunadem.datasets", "load_kaguya_scene"),
    "load_pds_label": ("lunadem.io.pds", "load_pds_label"),
    "load_stac_item": ("lunadem.datasets", "load_stac_item"),
    "m_to_km": ("lunadem.geometry.conversions", "m_to_km"),
    "m_to_mm": ("lunadem.geometry.conversions", "m_to_mm"),
    "mean_vector": ("lunadem.geometry.conversions", "mean_vector"),
    "mm_to_m": ("lunadem.geometry.conversions", "mm_to_m"),
    "normalize_to_unit_range": ("lunadem.utils.arrays", "normalize_to_unit_range"),
    "path_length": ("lunadem.geometry.conversions", "path_length"),
    "pixel_scale_meters": ("lunadem.geometry.scaling", "pixel_scale_meters"),
    "pixel_to_projected": ("lunadem.geometry.conversions", "pixel_to_projected"),
    "plot_moon_surface_3d": ("lunadem.visualization", "plot_moon_surface_3d"),
    "plot_3d_surface": ("lunadem.visualization.plots", "plot_3d_surface"),
    "plot_3d_surface_interactive": ("lunadem.visualization", "plot_3d_surface_interactive"),
    "plot_depth_map": ("lunadem.visualization.plots", "plot_depth_map"),
    "plot_landing_site_2d": ("lunadem.visualization", "plot_landing_site_2d"),
    "plot_landing_site_3d": ("lunadem.visualization", "plot_landing_site_3d"),
    "plot_scene_geometry_3d": ("lunadem.visualization", "plot_scene_geometry_3d"),
    "predict_illumination": ("lunadem.ml", "predict_illumination"),
    "predict_scene_location": ("lunadem.ml", "predict_scene_location"),
    "predict_scene_metadata": ("lunadem.ml", "predict_scene_metadata"),
    "predict_view_geometry": ("lunadem.ml", "predict_view_geometry"),
    "projected_to_pixel": ("lunadem.geometry.conversions", "projected_to_pixel"),
    "rad_to_deg": ("lunadem.geometry.conversions", "rad_to_deg"),
    "scale_dem_to_meters": ("lunadem.geometry.scaling", "scale_dem_to_meters"),
    "save_dem_as_geotiff": ("lunadem.io.raster", "save_dem_as_geotiff"),
    "save_dem_as_obj": ("lunadem.io.mesh", "save_dem_as_obj"),
    "save_dem_as_ply": ("lunadem.io.mesh", "save_dem_as_ply"),
    "save_manifest": ("lunadem.io.manifest", "save_manifest"),
    "scene_geometry_to_dict": ("lunadem.datasets", "scene_geometry_to_dict"),
    "show_depth_map": ("lunadem.visualization", "show_depth_map"),
    "show_landing_site_2d": ("lunadem.visualization", "show_landing_site_2d"),
    "show_landing_site_3d": ("lunadem.visualization", "show_landing_site_3d"),
    "show_moon_surface_3d": ("lunadem.visualization", "show_moon_surface_3d"),
    "show_scene_geometry_3d": ("lunadem.visualization", "show_scene_geometry_3d"),
    "show_surface_3d": ("lunadem.visualization", "show_surface_3d"),
    "summarize_scene_metadata": ("lunadem.datasets", "summarize_scene_metadata"),
}

__all__ = ["__version__", *_EXPORT_MAP.keys()]


def __getattr__(name: str):
    if name not in _EXPORT_MAP:
        raise AttributeError(f"module 'lunadem' has no attribute {name!r}")
    module_name, attribute_name = _EXPORT_MAP[name]
    module = import_module(module_name)
    value = getattr(module, attribute_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(__all__)
