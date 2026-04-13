"""Dataset access helpers for packaged lunar scene metadata."""

from __future__ import annotations

from importlib import import_module

_EXPORT_MAP = {
    "TEST_SCENE_ID": ("lunadem.datasets.kaguya", "TEST_SCENE_ID"),
    "build_scene_summary": ("lunadem.datasets.kaguya", "build_scene_summary"),
    "download_test_scene": ("lunadem.datasets.kaguya", "download_test_scene"),
    "get_scene_bbox": ("lunadem.datasets.kaguya", "get_scene_bbox"),
    "get_scene_camera_summary": ("lunadem.datasets.kaguya", "get_scene_camera_summary"),
    "get_scene_centroid": ("lunadem.datasets.kaguya", "get_scene_centroid"),
    "get_scene_footprint_lonlat": ("lunadem.datasets.kaguya", "get_scene_footprint_lonlat"),
    "get_scene_footprint_xyz": ("lunadem.datasets.kaguya", "get_scene_footprint_xyz"),
    "get_scene_ground_area_km2": ("lunadem.datasets.kaguya", "get_scene_ground_area_km2"),
    "get_scene_ground_coverage": ("lunadem.datasets.kaguya", "get_scene_ground_coverage"),
    "get_scene_sun_summary": ("lunadem.datasets.kaguya", "get_scene_sun_summary"),
    "get_scene_sun_vector": ("lunadem.datasets.kaguya", "get_scene_sun_vector"),
    "get_scene_time_range": ("lunadem.datasets.kaguya", "get_scene_time_range"),
    "get_scene_transform": ("lunadem.datasets.kaguya", "get_scene_transform"),
    "get_scene_view_angles": ("lunadem.datasets.kaguya", "get_scene_view_angles"),
    "get_test_scene_manifest": ("lunadem.datasets.kaguya", "get_test_scene_manifest"),
    "list_kaguya_scenes": ("lunadem.datasets.kaguya", "list_kaguya_scenes"),
    "load_camera_model": ("lunadem.datasets.kaguya", "load_camera_model"),
    "load_kaguya_scene": ("lunadem.datasets.kaguya", "load_kaguya_scene"),
    "load_stac_item": ("lunadem.datasets.kaguya", "load_stac_item"),
    "scene_geometry_to_dict": ("lunadem.datasets.kaguya", "scene_geometry_to_dict"),
    "summarize_scene_metadata": ("lunadem.datasets.kaguya", "summarize_scene_metadata"),
}

__all__ = list(_EXPORT_MAP)


def __getattr__(name: str):
    if name not in _EXPORT_MAP:
        raise AttributeError(f"module 'lunadem.datasets' has no attribute {name!r}")
    module_name, attribute_name = _EXPORT_MAP[name]
    module = import_module(module_name)
    value = getattr(module, attribute_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(__all__)
