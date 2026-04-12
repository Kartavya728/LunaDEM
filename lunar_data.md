# Kaguya Lunar Data Notes

This file explains the main terms present in the Kaguya dataset files stored under `dataset/<scene-id>/`.

## Folder Layout

- `stac/item.json`: STAC scene metadata
- `metadata/camera.json`: detailed camera, pose, and sun geometry
- `metadata/caminfo.pvl`: camera-model export
- `metadata/pds.lbl`: PDS label
- `metadata/isis.lbl`: ISIS label
- `metadata/provenance.txt`: provenance notes
- `image/image.tif`: main lunar image
- `preview/thumbnail.jpg`: preview image

## Important STAC Fields

### `id`

Unique scene identifier.

API:

- `load_stac_item(...)`
- `load_kaguya_scene(...)`

### `properties.gsd`

Ground sample distance in meters per pixel.

API:

- `summarize_scene_metadata(...)`
- `predict_scene_location(...)`

### `properties.proj:shape`

Image shape as `[rows, cols]`.

API:

- `summarize_scene_metadata(...)`
- `ground_coverage_meters(...)`

### `properties.proj:transform`

Projected affine transform. This lets the library convert between pixel coordinates and projected coordinates.

API:

- `pixel_to_projected(...)`
- `projected_to_pixel(...)`

### `properties.proj:centroid`

Approximate center latitude and longitude.

API:

- `summarize_scene_metadata(...)`
- `latlon_to_cartesian_moon(...)`
- `cartesian_to_latlon_moon(...)`
- `predict_scene_location(...)`

### `properties.view:sun_azimuth` and `properties.view:sun_elevation`

Sun direction used for shading geometry.

API:

- `get_light_vector(...)`
- `summarize_scene_metadata(...)`
- `predict_illumination(...)`

### `properties.view:off_nadir` and `properties.view:azimuth`

Camera look geometry.

API:

- `summarize_scene_metadata(...)`
- `predict_view_geometry(...)`

## Important `camera.json` Fields

### `image_lines`, `image_samples`

Line-scan image dimensions from the camera model.

API:

- `summarize_scene_metadata(...)`
- `line_time_seconds(...)`

### `instrument_position.positions`

Camera position path over the acquisition.

API:

- `summarize_scene_metadata(...)`
- `plot_scene_geometry_3d(...)`

### `instrument_pointing.quaternions`

Camera orientation history.

Use:

- orientation diagnostics
- future camera-frustum refinement

### `sun_position.positions`

Sun position vectors from the camera model.

API:

- `summarize_scene_metadata(...)`
- `plot_scene_geometry_3d(...)`

### `optical_distortion`

Lens distortion coefficients for the terrain camera model.

Use:

- camera calibration
- future geometric refinement workflows

## Derived Values In lunadem

`lunadem` can derive the following values without guessing:

- acquisition duration
- approximate line time
- ground width and height
- angular bbox area
- approximate lunar bbox area in square kilometers
- centroid XYZ position on the Moon
- pixel to projected coordinates and back
- mean camera position
- mean sun position
- camera path length
- sun unit vector

## Main Functions

```python
from lunadem import (
    bbox_area_km2,
    load_camera_model,
    load_kaguya_scene,
    load_stac_item,
    pixel_to_projected,
    summarize_scene_metadata,
)

item = load_stac_item("TC1S2B0_01_07496N087E3020")
camera = load_camera_model("TC1S2B0_01_07496N087E3020")
scene = load_kaguya_scene("TC1S2B0_01_07496N087E3020")
geometry = summarize_scene_metadata(item, camera)

print(scene.scene_id)
print(geometry.gsd_m)
print(geometry.mean_camera_distance_km)
print(pixel_to_projected(100, 120, geometry.transform))
print(bbox_area_km2(geometry.bbox_deg, geometry.centroid_lat_deg))
```
