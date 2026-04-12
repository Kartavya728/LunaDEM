"""Kaguya dataset loading, derivation, and download helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping, MutableMapping

import numpy as np
import requests

from lunadem.core.models import KaguyaScene, SceneGeometry
from lunadem.geometry.conversions import (
    acquisition_duration_seconds,
    bbox_area_deg2,
    bbox_area_km2,
    ground_coverage_meters,
    latlon_to_cartesian_moon,
    line_time_seconds,
    mean_vector,
    path_length,
)
from lunadem.geometry.lighting import get_light_vector

DEFAULT_DATASET_ROOT = Path("dataset")
TEST_SCENE_ID = "TC1S2B0_01_07496N087E3020"


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_scene_dir(scene_id_or_path: str | Path, dataset_root: str | Path = DEFAULT_DATASET_ROOT) -> Path:
    path = Path(scene_id_or_path)
    if path.is_file():
        return path.parent.parent if path.name == "item.json" else path.parent
    if path.is_dir():
        return path
    candidate = Path(dataset_root) / str(scene_id_or_path)
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"Scene directory not found for {scene_id_or_path!r}")


def load_stac_item(scene_id_or_path: str | Path, dataset_root: str | Path = DEFAULT_DATASET_ROOT) -> Dict[str, Any]:
    """Load a STAC item.json from the local Kaguya dataset."""
    path = Path(scene_id_or_path)
    if path.is_file():
        return _load_json(path)
    scene_dir = _resolve_scene_dir(scene_id_or_path, dataset_root=dataset_root)
    return _load_json(scene_dir / "stac" / "item.json")


def load_camera_model(scene_id_or_path: str | Path, dataset_root: str | Path = DEFAULT_DATASET_ROOT) -> Dict[str, Any]:
    """Load a camera.json model from the local Kaguya dataset."""
    path = Path(scene_id_or_path)
    if path.is_file():
        return _load_json(path)
    scene_dir = _resolve_scene_dir(scene_id_or_path, dataset_root=dataset_root)
    return _load_json(scene_dir / "metadata" / "camera.json")


def summarize_scene_metadata(
    item: Mapping[str, Any] | str | Path,
    camera_model: Mapping[str, Any] | str | Path | None = None,
) -> SceneGeometry:
    """Derive scene geometry from STAC and camera-model metadata."""
    if not isinstance(item, Mapping):
        item = load_stac_item(item)
    if camera_model is not None and not isinstance(camera_model, Mapping):
        camera_model = load_camera_model(camera_model)

    properties = item.get("properties", {})
    centroid = properties.get("proj:centroid", {})
    shape = properties.get("proj:shape")
    bbox = item.get("bbox") or properties.get("proj:bbox")
    gsd_m = properties.get("gsd")
    acquisition_duration_s = None
    line_time_s_value = None

    if properties.get("start_datetime") and properties.get("end_datetime"):
        acquisition_duration_s = acquisition_duration_seconds(
            properties["start_datetime"],
            properties["end_datetime"],
        )

    image_shape = None
    if shape and len(shape) >= 2:
        image_shape = (int(shape[0]), int(shape[1]))

    if acquisition_duration_s is not None and image_shape is not None:
        line_source = image_shape[0]
        if camera_model:
            line_source = int(camera_model.get("image_lines", line_source))
        line_time_s_value = line_time_seconds(acquisition_duration_s, line_source)

    ground_height_m = ground_width_m = ground_area_km2_value = None
    if image_shape is not None and gsd_m is not None:
        ground_height_m, ground_width_m = ground_coverage_meters(image_shape, float(gsd_m))
        ground_area_km2_value = float((ground_height_m * ground_width_m) / 1_000_000.0)

    bbox_deg2_value = bbox_area_km2_value = None
    if bbox is not None:
        bbox_deg2_value = bbox_area_deg2(bbox)
        lat_center = float(centroid.get("lat", 0.0))
        bbox_area_km2_value = bbox_area_km2(bbox, lat_center)

    footprint_lonlat = []
    footprint_xyz = []
    geometry = item.get("geometry", {})
    coordinates = geometry.get("coordinates", [])
    if coordinates:
        ring = coordinates[0]
        for lon, lat in ring:
            footprint_lonlat.append((float(lon), float(lat)))
            footprint_xyz.append(latlon_to_cartesian_moon(float(lat), float(lon)))

    sun_vector = None
    if properties.get("view:sun_azimuth") is not None and properties.get("view:sun_elevation") is not None:
        sun_vector = get_light_vector(
            float(properties["view:sun_azimuth"]),
            float(properties["view:sun_elevation"]),
        )

    mean_camera_position = None
    mean_camera_velocity = None
    mean_camera_distance = None
    mean_sun_position = None
    mean_sun_distance = None
    camera_path_length_km = None
    if camera_model:
        instrument_position = camera_model.get("instrument_position", {})
        sun_position = camera_model.get("sun_position", {})
        camera_positions = instrument_position.get("positions", [])
        camera_velocities = instrument_position.get("velocities", [])
        sun_positions = sun_position.get("positions", [])
        mean_camera_position = mean_vector(camera_positions)
        mean_camera_velocity = mean_vector(camera_velocities)
        mean_sun_position = mean_vector(sun_positions)
        if mean_camera_position is not None:
            mean_camera_distance = float(np.linalg.norm(mean_camera_position))
        if mean_sun_position is not None:
            mean_sun_distance = float(np.linalg.norm(mean_sun_position))
        camera_path_length_km = path_length(camera_positions)

    transform = properties.get("proj:transform")
    return SceneGeometry(
        acquisition_duration_s=acquisition_duration_s,
        line_time_s=line_time_s_value,
        centroid_lat_deg=float(centroid["lat"]) if "lat" in centroid else None,
        centroid_lon_deg=float(centroid["lon"]) if "lon" in centroid else None,
        bbox_deg=tuple(float(value) for value in bbox) if bbox is not None else None,
        bbox_area_deg2=bbox_deg2_value,
        bbox_area_km2=bbox_area_km2_value,
        gsd_m=float(gsd_m) if gsd_m is not None else None,
        image_shape=image_shape,
        ground_width_m=ground_width_m,
        ground_height_m=ground_height_m,
        ground_area_km2=ground_area_km2_value,
        transform=tuple(float(value) for value in transform) if transform is not None else None,
        sun_vector=sun_vector,
        mean_camera_position_km=mean_camera_position,
        mean_camera_velocity_km_s=mean_camera_velocity,
        mean_camera_distance_km=mean_camera_distance,
        mean_sun_position_km=mean_sun_position,
        mean_sun_distance_km=mean_sun_distance,
        camera_path_length_km=camera_path_length_km,
        view_azimuth_deg=float(properties["view:azimuth"]) if properties.get("view:azimuth") is not None else None,
        off_nadir_deg=float(properties["view:off_nadir"]) if properties.get("view:off_nadir") is not None else None,
        footprint_lonlat=footprint_lonlat,
        footprint_xyz_m=footprint_xyz,
    )


def load_kaguya_scene(
    scene_id_or_path: str | Path = TEST_SCENE_ID,
    dataset_root: str | Path = DEFAULT_DATASET_ROOT,
) -> KaguyaScene:
    """Load a complete local Kaguya scene bundle."""
    scene_dir = _resolve_scene_dir(scene_id_or_path, dataset_root=dataset_root)
    item_path = scene_dir / "stac" / "item.json"
    camera_path = scene_dir / "metadata" / "camera.json"
    image_path = scene_dir / "image" / "image.tif"
    thumbnail_path = scene_dir / "preview" / "thumbnail.jpg"

    item = load_stac_item(item_path)
    camera_model = load_camera_model(camera_path)
    geometry = summarize_scene_metadata(item, camera_model)
    return KaguyaScene(
        scene_id=item["id"],
        scene_dir=scene_dir,
        item_path=item_path,
        camera_path=camera_path,
        image_path=image_path,
        thumbnail_path=thumbnail_path if thumbnail_path.exists() else None,
        stac_item=item,
        camera_model=camera_model,
        geometry=geometry,
    )


def get_test_scene_manifest(dataset_root: str | Path = DEFAULT_DATASET_ROOT) -> Dict[str, Any]:
    """Return the local manifest for the packaged reference scene."""
    scene = load_kaguya_scene(TEST_SCENE_ID, dataset_root=dataset_root)
    item = scene.stac_item
    assets = item.get("assets", {})
    return {
        "scene_id": scene.scene_id,
        "scene_dir": str(scene.scene_dir),
        "item_path": str(scene.item_path),
        "camera_path": str(scene.camera_path),
        "image_path": str(scene.image_path),
        "thumbnail_path": str(scene.thumbnail_path) if scene.thumbnail_path else None,
        "assets": {
            key: {
                "href": value.get("href"),
                "type": value.get("type"),
                "title": value.get("title"),
            }
            for key, value in assets.items()
        },
        "geometry": scene.geometry,
    }


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _download_file(url: str, destination: Path, overwrite: bool = False, timeout_s: float = 60.0) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not overwrite:
        return destination
    response = requests.get(url, timeout=timeout_s)
    response.raise_for_status()
    destination.write_bytes(response.content)
    return destination


def download_test_scene(
    output_dir: str | Path,
    overwrite: bool = False,
    dataset_root: str | Path = DEFAULT_DATASET_ROOT,
    timeout_s: float = 60.0,
) -> Dict[str, str]:
    """Download the official test scene bundle to a target directory."""
    scene = load_kaguya_scene(TEST_SCENE_ID, dataset_root=dataset_root)
    item = scene.stac_item
    assets = item.get("assets", {})
    destination_root = Path(output_dir) / TEST_SCENE_ID
    destination_root.mkdir(parents=True, exist_ok=True)

    _write_json(destination_root / "stac" / "item.json", item)

    downloads: MutableMapping[str, str] = {}
    asset_map = {
        "image": destination_root / "image" / "image.tif",
        "thumbnail": destination_root / "preview" / "thumbnail.jpg",
        "caminfo_pvl": destination_root / "metadata" / "caminfo.pvl",
        "usgscsm_isd": destination_root / "metadata" / "camera.json",
        "pds_label": destination_root / "metadata" / "pds.lbl",
        "isis_label": destination_root / "metadata" / "isis.lbl",
        "provenance": destination_root / "metadata" / "provenance.txt",
    }

    for key, destination in asset_map.items():
        asset = assets.get(key)
        if not asset or not asset.get("href"):
            continue
        downloads[key] = str(_download_file(asset["href"], destination, overwrite=overwrite, timeout_s=timeout_s))

    return dict(downloads)
