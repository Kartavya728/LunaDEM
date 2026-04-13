# Run Guide For lunadem

This guide is generated from the installed `lunadem` API surface.

## Quick Scene

- Official test scene: `TC1S2B0_01_07496N087E3020`
- Local scene folders discovered: `TC1S2B0_01_07495N079E3030, TC1S2B0_01_07495N088E3030, TC1S2B0_01_07495N102E3030, TC1S2B0_01_07495N116E3030, TC1S2B0_01_07495N130E3030, TC1S2B0_01_07495N143E3030, TC1S2B0_01_07495N157E3031, TC1S2B0_01_07495N171E3031, TC1S2B0_01_07495N184E3031, TC1S2B0_01_07496N077E3020, TC1S2B0_01_07496N087E3020, TC1S2B0_01_07496N101E3020, TC1S2B0_01_07496N115E3020, TC1S2B0_01_07496N128E3020, TC1S2B0_01_07496N142E3020, TC1S2B0_01_07496N156E3020, TC1S2B0_01_07496N169E3020, TC1S2B0_01_07496N183E3021`
- Built-in rover presets: `curiosity, opportunity, perseverance, pragyan, sojourner, soraq, spirit`

## Main CLI Commands

```bash
lunadem download --test --output downloads
lunadem scene-summary TC1S2B0_01_07496N087E3020
lunadem sfs --maths
lunadem predict dataset/TC1S2B0_01_07496N087E3020/image/image.tif --kind all
lunadem generate dataset/TC1S2B0_01_07496N087E3020/image/image.tif --method hybrid --output output
lunadem plot-surface dataset/TC1S2B0_01_07496N087E3020/image/image.tif --backend both --show --reconstruct
lunadem plot-scene TC1S2B0_01_07496N087E3020 --backend both --show --output output/scene_geometry.png --output-html output/scene_geometry.html
lunadem landing-site dataset/TC1S2B0_01_07496N087E3020/image/image.tif --scene TC1S2B0_01_07496N087E3020 --rover pragyan --backend both --show --output-2d output/landing_2d.png --output-3d output/landing_3d.png --output-2d-html output/landing_2d.html --output-3d-html output/landing_3d.html
```

## Standard Python Workflow

```python
from lunadem import (
    build_scene_summary,
    find_safe_landing_site,
    generate_dem,
    get_rover_spec,
    load_kaguya_scene,
    plot_landing_site_2d,
    plot_landing_site_3d,
    plot_moon_surface_3d,
    plot_scene_geometry_3d,
    predict_scene_metadata,
)

scene = load_kaguya_scene('TC1S2B0_01_07496N087E3020')
summary = build_scene_summary(scene)
prediction = predict_scene_metadata(scene.image_path)
dem = generate_dem(scene.image_path, method='hybrid')
landing = find_safe_landing_site(scene.image_path, rover=get_rover_spec('pragyan'), scene=scene)
plot_scene_geometry_3d(scene, backend='both', show=False, save_path='output/scene_geometry.png', html_path='output/scene_geometry.html')
plot_moon_surface_3d(scene, backend='both', show=False, save_path='output/moon_surface.png', html_path='output/moon_surface.html')
plot_landing_site_2d(scene.image_path, landing, backend='both', show=False, save_path='output/landing_2d.png', html_path='output/landing_2d.html')
plot_landing_site_3d(scene.image_path, landing, backend='both', show=False, save_path='output/landing_3d.png', html_path='output/landing_3d.html')
print(summary['centroid'])
print(prediction.targets)
print(landing.summary)
```

## Function Catalog

The current public API exposes `82` callable functions and helpers. The list below documents more than 30 of them.

### 1. `acquisition_duration_seconds`

- Purpose: Compute acquisition duration in seconds from ISO timestamps.
- Import: `from lunadem import acquisition_duration_seconds`
- Signature: `acquisition_duration_seconds(start_datetime: 'str', end_datetime: 'str') -> 'float'`
- Returns: `float`
- Parameter `start_datetime`: str
- Parameter `end_datetime`: str
- Example:
```python
from lunadem import acquisition_duration_seconds
result = acquisition_duration_seconds(...)
print(result)
```

### 2. `analyze_dem`

- Purpose: Analyze an existing DEM.
- Import: `from lunadem import analyze_dem`
- Signature: `analyze_dem(dem_or_path: 'np.ndarray | str | Path', analysis_config: 'AnalysisConfig | Dict[str, Any] | None' = None) -> 'TerrainMetrics'`
- Returns: `TerrainMetrics`
- Parameter `dem_or_path`: np.ndarray | str | Path
- Parameter `analysis_config`: AnalysisConfig | Dict[str, Any] | None
- Example:
```python
from lunadem import analyze_dem
result = analyze_dem(...)
print(result)
```

### 3. `assess_landing`

- Purpose: Assess landing suitability for a DEM.
- Import: `from lunadem import assess_landing`
- Signature: `assess_landing(dem_or_path: 'np.ndarray | str | Path', landing_config: 'LandingConfig | Dict[str, Any] | None' = None, analysis_config: 'AnalysisConfig | Dict[str, Any] | None' = None) -> 'LandingReport'`
- Returns: `LandingReport`
- Parameter `dem_or_path`: np.ndarray | str | Path
- Parameter `landing_config`: LandingConfig | Dict[str, Any] | None
- Parameter `analysis_config`: AnalysisConfig | Dict[str, Any] | None
- Example:
```python
from lunadem import assess_landing
result = assess_landing(...)
print(result)
```

### 4. `bbox_area_deg2`

- Purpose: Approximate angular area of a lon/lat bbox in square degrees.
- Import: `from lunadem import bbox_area_deg2`
- Signature: `bbox_area_deg2(bbox: 'Sequence[float]') -> 'float'`
- Returns: `float`
- Parameter `bbox`: Sequence[float]
- Example:
```python
from lunadem import bbox_area_deg2
result = bbox_area_deg2(...)
print(result)
```

### 5. `bbox_area_km2`

- Purpose: Approximate lunar surface area of a lon/lat bbox in square kilometers.
- Import: `from lunadem import bbox_area_km2`
- Signature: `bbox_area_km2(bbox: 'Sequence[float]', lat_center_deg: 'float', radius_m: 'float' = 1737400.0) -> 'float'`
- Returns: `float`
- Parameter `bbox`: Sequence[float]
- Parameter `lat_center_deg`: float
- Parameter `radius_m`: float
- Example:
```python
from lunadem import bbox_area_km2
result = bbox_area_km2(...)
print(result)
```

### 6. `build_scene_summary`

- Purpose: Build a JSON-ready summary of the scene metadata and derived geometry.
- Import: `from lunadem import build_scene_summary`
- Signature: `build_scene_summary(scene_or_geometry_or_item: 'KaguyaScene | SceneGeometry | Mapping[str, Any] | str | Path', camera_model: 'Mapping[str, Any] | str | Path | None' = None) -> 'Dict[str, Any]'`
- Returns: `Dict[str, Any]`
- Parameter `scene_or_geometry_or_item`: KaguyaScene | SceneGeometry | Mapping[str, Any] | str | Path
- Parameter `camera_model`: Mapping[str, Any] | str | Path | None
- Example:
```python
from lunadem import build_scene_summary, load_kaguya_scene
scene = load_kaguya_scene('TC1S2B0_01_07496N087E3020')
summary = build_scene_summary(scene)
print(summary['centroid'])
```

### 7. `calculate_predicted_image`

- Purpose: Compute Lambertian reflectance image from height map.
- Import: `from lunadem import calculate_predicted_image`
- Signature: `calculate_predicted_image(height_map: 'np.ndarray', light_vec: 'np.ndarray') -> 'np.ndarray'`
- Returns: `np.ndarray`
- Parameter `height_map`: np.ndarray
- Parameter `light_vec`: np.ndarray
- Example:
```python
from lunadem import calculate_predicted_image
result = calculate_predicted_image(...)
print(result)
```

### 8. `calculate_surface_normals`

- Purpose: Calculate normalized surface normals from DEM.
- Import: `from lunadem import calculate_surface_normals`
- Signature: `calculate_surface_normals(height_map: 'np.ndarray') -> 'np.ndarray'`
- Returns: `np.ndarray`
- Parameter `height_map`: np.ndarray
- Example:
```python
from lunadem import calculate_surface_normals
result = calculate_surface_normals(...)
print(result)
```

### 9. `cartesian_to_latlon_moon`

- Purpose: Convert Cartesian coordinates to lunar latitude/longitude and radius.
- Import: `from lunadem import cartesian_to_latlon_moon`
- Signature: `cartesian_to_latlon_moon(x_m: 'float', y_m: 'float', z_m: 'float') -> 'Tuple[float, float, float]'`
- Returns: `Tuple[float, float, float]`
- Parameter `x_m`: float
- Parameter `y_m`: float
- Parameter `z_m`: float
- Example:
```python
from lunadem import cartesian_to_latlon_moon
result = cartesian_to_latlon_moon(...)
print(result)
```

### 10. `deg_to_rad`

- Purpose: Convert degrees to radians.
- Import: `from lunadem import deg_to_rad`
- Signature: `deg_to_rad(value_deg: 'float') -> 'float'`
- Returns: `float`
- Parameter `value_deg`: float
- Example:
```python
from lunadem import deg_to_rad
result = deg_to_rad(...)
print(result)
```

### 11. `download_test_scene`

- Purpose: Download the official test scene bundle to a target directory.
- Import: `from lunadem import download_test_scene`
- Signature: `download_test_scene(output_dir: 'str | Path', overwrite: 'bool' = False, dataset_root: 'str | Path' = WindowsPath('dataset'), timeout_s: 'float' = 60.0) -> 'Dict[str, str]'`
- Returns: `Dict[str, str]`
- Parameter `output_dir`: str | Path
- Parameter `overwrite`: bool
- Parameter `dataset_root`: str | Path
- Parameter `timeout_s`: float
- Example:
```python
from lunadem import download_test_scene
downloads = download_test_scene('downloads', overwrite=False)
print(downloads)
```

### 12. `ensure_directory`

- Purpose: Create a directory when missing and return it as a Path.
- Import: `from lunadem import ensure_directory`
- Signature: `ensure_directory(path: 'str | Path') -> 'Path'`
- Returns: `Path`
- Parameter `path`: str | Path
- Example:
```python
from lunadem import ensure_directory
result = ensure_directory(...)
print(result)
```

### 13. `extract_pds_geometry`

- Purpose: Extract common geometry fields from parsed label dictionary.
- Import: `from lunadem import extract_pds_geometry`
- Signature: `extract_pds_geometry(label: 'Dict[str, Any]') -> 'Dict[str, Any]'`
- Returns: `Dict[str, Any]`
- Parameter `label`: Dict[str, Any]
- Example:
```python
from lunadem import extract_pds_geometry
result = extract_pds_geometry(...)
print(result)
```

### 14. `find_safe_landing_site`

- Purpose: Find the safest landing site for a rover on an image or DEM.
- Import: `from lunadem import find_safe_landing_site`
- Signature: `find_safe_landing_site(image_or_dem: 'np.ndarray | str | Path', *, rover: 'str | RoverSpec | Mapping[str, Any] | None' = None, scene: 'Any' = None, sun: 'Any' = None, camera: 'Mapping[str, Any] | None' = None, time: 'str | None' = None, method: 'str' = 'hybrid', reconstruct: 'bool | None' = None, config: 'ReconstructionConfig | Mapping[str, Any] | None' = None, analysis_config: 'AnalysisConfig | Mapping[str, Any] | None' = None, landing_config: 'LandingConfig | Mapping[str, Any] | None' = None) -> 'LandingSiteResult'`
- Returns: `LandingSiteResult`
- Parameter `image_or_dem`: np.ndarray | str | Path
- Parameter `rover`: str | RoverSpec | Mapping[str, Any] | None
- Parameter `scene`: Any
- Parameter `sun`: Any
- Parameter `camera`: Mapping[str, Any] | None
- Parameter `time`: str | None
- Parameter `method`: str
- Parameter `reconstruct`: bool | None
- Parameter `config`: ReconstructionConfig | Mapping[str, Any] | None
- Parameter `analysis_config`: AnalysisConfig | Mapping[str, Any] | None
- Parameter `landing_config`: LandingConfig | Mapping[str, Any] | None
- Example:
```python
from lunadem import find_safe_landing_site, get_rover_spec, load_kaguya_scene
scene = load_kaguya_scene('TC1S2B0_01_07496N087E3020')
landing = find_safe_landing_site(scene.image_path, rover=get_rover_spec('pragyan'), scene=scene)
print(landing.summary)
```

### 15. `generate_dem`

- Purpose: Generate a DEM from image input.
- Import: `from lunadem import generate_dem`
- Signature: `generate_dem(input_data: 'np.ndarray | str | Path', method: 'str' = 'sfs', config: 'ReconstructionConfig | Dict[str, Any] | None' = None, analysis_config: 'AnalysisConfig | Dict[str, Any] | None' = None) -> 'DEMResult'`
- Returns: `DEMResult`
- Parameter `input_data`: np.ndarray | str | Path
- Parameter `method`: str
- Parameter `config`: ReconstructionConfig | Dict[str, Any] | None
- Parameter `analysis_config`: AnalysisConfig | Dict[str, Any] | None
- Example:
```python
from lunadem import ReconstructionConfig, generate_dem
config = ReconstructionConfig(output={'output_dir': 'output', 'base_name': 'demo'})
result = generate_dem('dataset/TC1S2B0_01_07496N087E3020/image/image.tif', method='hybrid', config=config)
print(result.dem_meters.shape)
```

### 16. `get_light_vector`

- Purpose: Convert sun azimuth/elevation to a unit light vector.
- Import: `from lunadem import get_light_vector`
- Signature: `get_light_vector(sun_azimuth_deg: 'float', sun_elevation_deg: 'float') -> 'np.ndarray'`
- Returns: `np.ndarray`
- Parameter `sun_azimuth_deg`: float
- Parameter `sun_elevation_deg`: float
- Example:
```python
from lunadem import get_light_vector
result = get_light_vector(...)
print(result)
```

### 17. `get_model_artifact_paths`

- Purpose: Return the expected packaged ONNX artifact paths.
- Import: `from lunadem import get_model_artifact_paths`
- Signature: `get_model_artifact_paths() -> 'dict[str, str]'`
- Returns: `dict[str, str]`
- Example:
```python
from lunadem import get_model_artifact_paths
result = get_model_artifact_paths(...)
print(result)
```

### 18. `get_model_metrics`

- Purpose: Load packaged model metrics and scaling metadata.
- Import: `from lunadem import get_model_metrics`
- Signature: `get_model_metrics() -> 'Dict[str, Any]'`
- Returns: `Dict[str, Any]`
- Example:
```python
from lunadem import get_model_metrics
result = get_model_metrics(...)
print(result)
```

### 19. `get_model_targets`

- Purpose: Return the target names predicted by a given model.
- Import: `from lunadem import get_model_targets`
- Signature: `get_model_targets(model_name: 'str') -> 'tuple[str, ...]'`
- Returns: `tuple[str, ...]`
- Parameter `model_name`: str
- Example:
```python
from lunadem import get_model_targets
result = get_model_targets(...)
print(result)
```

### 20. `get_rover_spec`

- Purpose: Return a rover spec from a known name or custom dimensions.
- Import: `from lunadem import get_rover_spec`
- Signature: `get_rover_spec(name_or_custom_dims: 'str | RoverSpec | Mapping[str, Any] | None' = None, *, length_m: 'float | None' = None, width_m: 'float | None' = None, height_m: 'float | None' = None, ground_clearance_m: 'float | None' = None, safety_margin_m: 'float | None' = None) -> 'RoverSpec'`
- Returns: `RoverSpec`
- Parameter `name_or_custom_dims`: str | RoverSpec | Mapping[str, Any] | None
- Parameter `length_m`: float | None
- Parameter `width_m`: float | None
- Parameter `height_m`: float | None
- Parameter `ground_clearance_m`: float | None
- Parameter `safety_margin_m`: float | None
- Example:
```python
from lunadem import get_rover_spec
result = get_rover_spec(...)
print(result)
```

### 21. `get_scene_bbox`

- Purpose: Return the geographic bounding box for the scene.
- Import: `from lunadem import get_scene_bbox`
- Signature: `get_scene_bbox(scene_or_geometry_or_item: 'SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path', camera_model: 'Mapping[str, Any] | str | Path | None' = None) -> 'tuple[float, float, float, float] | None'`
- Returns: `tuple[float, float, float, float] | None`
- Parameter `scene_or_geometry_or_item`: SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path
- Parameter `camera_model`: Mapping[str, Any] | str | Path | None
- Example:
```python
from lunadem import get_scene_bbox
result = get_scene_bbox(...)
print(result)
```

### 22. `get_scene_camera_summary`

- Purpose: Return a compact summary of camera path and pose metadata.
- Import: `from lunadem import get_scene_camera_summary`
- Signature: `get_scene_camera_summary(scene_or_geometry_or_item: 'SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path', camera_model: 'Mapping[str, Any] | str | Path | None' = None) -> 'Dict[str, Any]'`
- Returns: `Dict[str, Any]`
- Parameter `scene_or_geometry_or_item`: SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path
- Parameter `camera_model`: Mapping[str, Any] | str | Path | None
- Example:
```python
from lunadem import get_scene_camera_summary
result = get_scene_camera_summary(...)
print(result)
```

### 23. `get_scene_centroid`

- Purpose: Return the centroid latitude and longitude in degrees.
- Import: `from lunadem import get_scene_centroid`
- Signature: `get_scene_centroid(scene_or_geometry_or_item: 'SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path', camera_model: 'Mapping[str, Any] | str | Path | None' = None) -> 'tuple[float | None, float | None]'`
- Returns: `tuple[float | None, float | None]`
- Parameter `scene_or_geometry_or_item`: SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path
- Parameter `camera_model`: Mapping[str, Any] | str | Path | None
- Example:
```python
from lunadem import get_scene_centroid
result = get_scene_centroid(...)
print(result)
```

### 24. `get_scene_footprint_lonlat`

- Purpose: Return the scene footprint polygon in longitude/latitude.
- Import: `from lunadem import get_scene_footprint_lonlat`
- Signature: `get_scene_footprint_lonlat(scene_or_geometry_or_item: 'SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path', camera_model: 'Mapping[str, Any] | str | Path | None' = None) -> 'list[tuple[float, float]]'`
- Returns: `list[tuple[float, float]]`
- Parameter `scene_or_geometry_or_item`: SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path
- Parameter `camera_model`: Mapping[str, Any] | str | Path | None
- Example:
```python
from lunadem import get_scene_footprint_lonlat
result = get_scene_footprint_lonlat(...)
print(result)
```

### 25. `get_scene_footprint_xyz`

- Purpose: Return the scene footprint polygon in Moon-centered Cartesian coordinates.
- Import: `from lunadem import get_scene_footprint_xyz`
- Signature: `get_scene_footprint_xyz(scene_or_geometry_or_item: 'SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path', camera_model: 'Mapping[str, Any] | str | Path | None' = None) -> 'list[tuple[float, float, float]]'`
- Returns: `list[tuple[float, float, float]]`
- Parameter `scene_or_geometry_or_item`: SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path
- Parameter `camera_model`: Mapping[str, Any] | str | Path | None
- Example:
```python
from lunadem import get_scene_footprint_xyz
result = get_scene_footprint_xyz(...)
print(result)
```

### 26. `get_scene_ground_area_km2`

- Purpose: Return the derived ground area covered by the scene in square kilometers.
- Import: `from lunadem import get_scene_ground_area_km2`
- Signature: `get_scene_ground_area_km2(scene_or_geometry_or_item: 'SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path', camera_model: 'Mapping[str, Any] | str | Path | None' = None) -> 'float | None'`
- Returns: `float | None`
- Parameter `scene_or_geometry_or_item`: SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path
- Parameter `camera_model`: Mapping[str, Any] | str | Path | None
- Example:
```python
from lunadem import get_scene_ground_area_km2
result = get_scene_ground_area_km2(...)
print(result)
```

### 27. `get_scene_ground_coverage`

- Purpose: Return ground coverage as (height_m, width_m).
- Import: `from lunadem import get_scene_ground_coverage`
- Signature: `get_scene_ground_coverage(scene_or_geometry_or_item: 'SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path', camera_model: 'Mapping[str, Any] | str | Path | None' = None) -> 'tuple[float | None, float | None]'`
- Returns: `tuple[float | None, float | None]`
- Parameter `scene_or_geometry_or_item`: SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path
- Parameter `camera_model`: Mapping[str, Any] | str | Path | None
- Example:
```python
from lunadem import get_scene_ground_coverage
result = get_scene_ground_coverage(...)
print(result)
```

### 28. `get_scene_sun_summary`

- Purpose: Return a compact summary of sun geometry metadata.
- Import: `from lunadem import get_scene_sun_summary`
- Signature: `get_scene_sun_summary(scene_or_geometry_or_item: 'SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path', camera_model: 'Mapping[str, Any] | str | Path | None' = None) -> 'Dict[str, Any]'`
- Returns: `Dict[str, Any]`
- Parameter `scene_or_geometry_or_item`: SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path
- Parameter `camera_model`: Mapping[str, Any] | str | Path | None
- Example:
```python
from lunadem import get_scene_sun_summary
result = get_scene_sun_summary(...)
print(result)
```

### 29. `get_scene_sun_vector`

- Purpose: Return the normalized sun vector derived from scene metadata.
- Import: `from lunadem import get_scene_sun_vector`
- Signature: `get_scene_sun_vector(scene_or_geometry_or_item: 'SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path', camera_model: 'Mapping[str, Any] | str | Path | None' = None) -> 'np.ndarray | None'`
- Returns: `np.ndarray | None`
- Parameter `scene_or_geometry_or_item`: SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path
- Parameter `camera_model`: Mapping[str, Any] | str | Path | None
- Example:
```python
from lunadem import get_scene_sun_vector
result = get_scene_sun_vector(...)
print(result)
```

### 30. `get_scene_time_range`

- Purpose: Return the scene acquisition time range from the STAC item.
- Import: `from lunadem import get_scene_time_range`
- Signature: `get_scene_time_range(item: 'Mapping[str, Any] | str | Path') -> 'tuple[str | None, str | None]'`
- Returns: `tuple[str | None, str | None]`
- Parameter `item`: Mapping[str, Any] | str | Path
- Example:
```python
from lunadem import get_scene_time_range
result = get_scene_time_range(...)
print(result)
```

### 31. `get_scene_transform`

- Purpose: Return the projected transform tuple when present.
- Import: `from lunadem import get_scene_transform`
- Signature: `get_scene_transform(scene_or_geometry_or_item: 'SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path', camera_model: 'Mapping[str, Any] | str | Path | None' = None) -> 'tuple[float, ...] | None'`
- Returns: `tuple[float, ...] | None`
- Parameter `scene_or_geometry_or_item`: SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path
- Parameter `camera_model`: Mapping[str, Any] | str | Path | None
- Example:
```python
from lunadem import get_scene_transform
result = get_scene_transform(...)
print(result)
```

### 32. `get_scene_view_angles`

- Purpose: Return view-angle metadata in degrees.
- Import: `from lunadem import get_scene_view_angles`
- Signature: `get_scene_view_angles(scene_or_geometry_or_item: 'SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path', camera_model: 'Mapping[str, Any] | str | Path | None' = None) -> 'Dict[str, float | None]'`
- Returns: `Dict[str, float | None]`
- Parameter `scene_or_geometry_or_item`: SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path
- Parameter `camera_model`: Mapping[str, Any] | str | Path | None
- Example:
```python
from lunadem import get_scene_view_angles
result = get_scene_view_angles(...)
print(result)
```

### 33. `get_sfs_assumptions`

- Purpose: Return the packaged SFS assumptions document.
- Import: `from lunadem import get_sfs_assumptions`
- Signature: `get_sfs_assumptions() -> 'str'`
- Returns: `str`
- Example:
```python
from lunadem import get_sfs_assumptions
result = get_sfs_assumptions(...)
print(result)
```

### 34. `get_sfs_math`

- Purpose: Return the packaged SFS mathematics document.
- Import: `from lunadem import get_sfs_math`
- Signature: `get_sfs_math() -> 'str'`
- Returns: `str`
- Example:
```python
from lunadem import get_sfs_math
result = get_sfs_math(...)
print(result)
```

### 35. `get_sfs_terms`

- Purpose: Return the packaged SFS terminology document.
- Import: `from lunadem import get_sfs_terms`
- Signature: `get_sfs_terms() -> 'str'`
- Returns: `str`
- Example:
```python
from lunadem import get_sfs_terms
result = get_sfs_terms(...)
print(result)
```

### 36. `get_test_scene_manifest`

- Purpose: Return the local manifest for the packaged reference scene.
- Import: `from lunadem import get_test_scene_manifest`
- Signature: `get_test_scene_manifest(dataset_root: 'str | Path' = WindowsPath('dataset')) -> 'Dict[str, Any]'`
- Returns: `Dict[str, Any]`
- Parameter `dataset_root`: str | Path
- Example:
```python
from lunadem import get_test_scene_manifest
result = get_test_scene_manifest(...)
print(result)
```

### 37. `ground_coverage_meters`

- Purpose: Return ground height/width in meters for an image shape and GSD.
- Import: `from lunadem import ground_coverage_meters`
- Signature: `ground_coverage_meters(shape: 'Sequence[int]', gsd_m: 'float') -> 'Tuple[float, float]'`
- Returns: `Tuple[float, float]`
- Parameter `shape`: Sequence[int]
- Parameter `gsd_m`: float
- Example:
```python
from lunadem import ground_coverage_meters
result = ground_coverage_meters(...)
print(result)
```

### 38. `km_to_m`

- Purpose: Convert kilometers to meters.
- Import: `from lunadem import km_to_m`
- Signature: `km_to_m(value_km: 'float') -> 'float'`
- Returns: `float`
- Parameter `value_km`: float
- Example:
```python
from lunadem import km_to_m
result = km_to_m(...)
print(result)
```

### 39. `latlon_to_cartesian_moon`

- Purpose: Convert lunar latitude/longitude to Cartesian coordinates.
- Import: `from lunadem import latlon_to_cartesian_moon`
- Signature: `latlon_to_cartesian_moon(lat_deg: 'float', lon_deg: 'float', radius_m: 'float' = 1737400.0) -> 'Tuple[float, float, float]'`
- Returns: `Tuple[float, float, float]`
- Parameter `lat_deg`: float
- Parameter `lon_deg`: float
- Parameter `radius_m`: float
- Example:
```python
from lunadem import latlon_to_cartesian_moon
result = latlon_to_cartesian_moon(...)
print(result)
```

### 40. `line_time_seconds`

- Purpose: Compute approximate line scan time from duration and line count.
- Import: `from lunadem import line_time_seconds`
- Signature: `line_time_seconds(duration_s: 'float', image_lines: 'int') -> 'float'`
- Returns: `float`
- Parameter `duration_s`: float
- Parameter `image_lines`: int
- Example:
```python
from lunadem import line_time_seconds
result = line_time_seconds(...)
print(result)
```

### 41. `list_available_rovers`

- Purpose: Return the sorted names of built-in rover presets.
- Import: `from lunadem import list_available_rovers`
- Signature: `list_available_rovers() -> 'list[str]'`
- Returns: `list[str]`
- Example:
```python
from lunadem import list_available_rovers
result = list_available_rovers(...)
print(result)
```

### 42. `list_kaguya_scenes`

- Purpose: Return sorted local scene identifiers available under the dataset root.
- Import: `from lunadem import list_kaguya_scenes`
- Signature: `list_kaguya_scenes(dataset_root: 'str | Path' = WindowsPath('dataset')) -> 'list[str]'`
- Returns: `list[str]`
- Parameter `dataset_root`: str | Path
- Example:
```python
from lunadem import list_kaguya_scenes
result = list_kaguya_scenes(...)
print(result)
```

### 43. `list_model_names`

- Purpose: Return the packaged metadata model names.
- Import: `from lunadem import list_model_names`
- Signature: `list_model_names() -> 'list[str]'`
- Returns: `list[str]`
- Example:
```python
from lunadem import list_model_names
result = list_model_names(...)
print(result)
```

### 44. `load_camera_model`

- Purpose: Load a camera.json model from the local Kaguya dataset.
- Import: `from lunadem import load_camera_model`
- Signature: `load_camera_model(scene_id_or_path: 'str | Path', dataset_root: 'str | Path' = WindowsPath('dataset')) -> 'Dict[str, Any]'`
- Returns: `Dict[str, Any]`
- Parameter `scene_id_or_path`: str | Path
- Parameter `dataset_root`: str | Path
- Example:
```python
from lunadem import load_camera_model
result = load_camera_model(...)
print(result)
```

### 45. `load_image`

- Purpose: Load PNG/JPG/TIFF/GeoTIFF or in-memory array.
- Import: `from lunadem import load_image`
- Signature: `load_image(image_input: 'str | Path | np.ndarray', normalize: 'bool' = True) -> 'Tuple[np.ndarray, Dict[str, Any]]'`
- Returns: `Tuple[np.ndarray, Dict[str, Any]]`
- Parameter `image_input`: str | Path | np.ndarray
- Parameter `normalize`: bool
- Example:
```python
from lunadem import load_image
result = load_image(...)
print(result)
```

### 46. `load_kaguya_scene`

- Purpose: Load a complete local Kaguya scene bundle.
- Import: `from lunadem import load_kaguya_scene`
- Signature: `load_kaguya_scene(scene_id_or_path: 'str | Path' = 'TC1S2B0_01_07496N087E3020', dataset_root: 'str | Path' = WindowsPath('dataset')) -> 'KaguyaScene'`
- Returns: `KaguyaScene`
- Parameter `scene_id_or_path`: str | Path
- Parameter `dataset_root`: str | Path
- Example:
```python
from lunadem import load_kaguya_scene
scene = load_kaguya_scene('TC1S2B0_01_07496N087E3020')
print(scene.scene_id)
print(scene.image_path)
```

### 47. `load_pds_label`

- Purpose: Load PDS label with optional `pvl` backend and fallback parser.
- Import: `from lunadem import load_pds_label`
- Signature: `load_pds_label(path: 'str | Path') -> 'Dict[str, Any]'`
- Returns: `Dict[str, Any]`
- Parameter `path`: str | Path
- Example:
```python
from lunadem import load_pds_label
result = load_pds_label(...)
print(result)
```

### 48. `load_stac_item`

- Purpose: Load a STAC item.json from the local Kaguya dataset.
- Import: `from lunadem import load_stac_item`
- Signature: `load_stac_item(scene_id_or_path: 'str | Path', dataset_root: 'str | Path' = WindowsPath('dataset')) -> 'Dict[str, Any]'`
- Returns: `Dict[str, Any]`
- Parameter `scene_id_or_path`: str | Path
- Parameter `dataset_root`: str | Path
- Example:
```python
from lunadem import load_stac_item
result = load_stac_item(...)
print(result)
```

### 49. `m_to_km`

- Purpose: Convert meters to kilometers.
- Import: `from lunadem import m_to_km`
- Signature: `m_to_km(value_m: 'float') -> 'float'`
- Returns: `float`
- Parameter `value_m`: float
- Example:
```python
from lunadem import m_to_km
result = m_to_km(...)
print(result)
```

### 50. `m_to_mm`

- Purpose: Convert meters to millimeters.
- Import: `from lunadem import m_to_mm`
- Signature: `m_to_mm(value_m: 'float') -> 'float'`
- Returns: `float`
- Parameter `value_m`: float
- Example:
```python
from lunadem import m_to_mm
result = m_to_mm(...)
print(result)
```

### 51. `mean_vector`

- Purpose: Return the arithmetic mean vector for a collection of numeric sequences.
- Import: `from lunadem import mean_vector`
- Signature: `mean_vector(values: 'Iterable[Sequence[float]]') -> 'np.ndarray | None'`
- Returns: `np.ndarray | None`
- Parameter `values`: Iterable[Sequence[float]]
- Example:
```python
from lunadem import mean_vector
result = mean_vector(...)
print(result)
```

### 52. `mm_to_m`

- Purpose: Convert millimeters to meters.
- Import: `from lunadem import mm_to_m`
- Signature: `mm_to_m(value_mm: 'float') -> 'float'`
- Returns: `float`
- Parameter `value_mm`: float
- Example:
```python
from lunadem import mm_to_m
result = mm_to_m(...)
print(result)
```

### 53. `normalize_to_unit_range`

- Purpose: Normalize an array to [0, 1].
- Import: `from lunadem import normalize_to_unit_range`
- Signature: `normalize_to_unit_range(array: 'np.ndarray') -> 'np.ndarray'`
- Returns: `np.ndarray`
- Parameter `array`: np.ndarray
- Example:
```python
from lunadem import normalize_to_unit_range
result = normalize_to_unit_range(...)
print(result)
```

### 54. `path_length`

- Purpose: Return the total Euclidean path length across sequential vectors.
- Import: `from lunadem import path_length`
- Signature: `path_length(values: 'Iterable[Sequence[float]]') -> 'float'`
- Returns: `float`
- Parameter `values`: Iterable[Sequence[float]]
- Example:
```python
from lunadem import path_length
result = path_length(...)
print(result)
```

### 55. `pixel_scale_meters`

- Purpose: Compute pixel ground sample distance in meters.
- Import: `from lunadem import pixel_scale_meters`
- Signature: `pixel_scale_meters(sensor: 'SensorConfig') -> 'float'`
- Returns: `float`
- Parameter `sensor`: SensorConfig
- Example:
```python
from lunadem import pixel_scale_meters
result = pixel_scale_meters(...)
print(result)
```

### 56. `pixel_to_projected`

- Purpose: Map pixel coordinates to projected coordinates using a GDAL transform.
- Import: `from lunadem import pixel_to_projected`
- Signature: `pixel_to_projected(row: 'float', col: 'float', transform: 'Sequence[float]') -> 'Tuple[float, float]'`
- Returns: `Tuple[float, float]`
- Parameter `row`: float
- Parameter `col`: float
- Parameter `transform`: Sequence[float]
- Example:
```python
from lunadem import pixel_to_projected
result = pixel_to_projected(...)
print(result)
```

### 57. `plot_3d_surface`

- Purpose: Render a 3D terrain surface with Matplotlib.
- Import: `from lunadem import plot_3d_surface`
- Signature: `plot_3d_surface(dem: 'np.ndarray', save_path: 'str | Path | None' = None, *, title: 'str' = 'Reconstructed 3D Surface', show: 'bool' = False, block: 'bool' = True, max_points: 'int' = 200)`
- Returns: `Any`
- Parameter `dem`: np.ndarray
- Parameter `save_path`: str | Path | None
- Parameter `title`: str
- Parameter `show`: bool
- Parameter `block`: bool
- Parameter `max_points`: int
- Example:
```python
from lunadem import plot_3d_surface
result = plot_3d_surface(...)
print(result)
```

### 58. `plot_3d_surface_interactive`

- Purpose: Render a hoverable 3D surface from a DEM or image-like array.
- Import: `from lunadem import plot_3d_surface_interactive`
- Signature: `plot_3d_surface_interactive(surface_or_image: 'np.ndarray | str | Path', *, title: 'str' = 'Interactive Lunar Surface', save_path: 'str | Path | None' = None, show: 'bool' = False) -> 'go.Figure'`
- Returns: `go.Figure`
- Parameter `surface_or_image`: np.ndarray | str | Path
- Parameter `title`: str
- Parameter `save_path`: str | Path | None
- Parameter `show`: bool
- Example:
```python
from lunadem import plot_3d_surface_interactive
result = plot_3d_surface_interactive(...)
print(result)
```

### 59. `plot_depth_map`

- Purpose: Render a 2D terrain map with Matplotlib.
- Import: `from lunadem import plot_depth_map`
- Signature: `plot_depth_map(dem: 'np.ndarray', save_path: 'str | Path | None' = None, *, title: 'str' = 'Reconstructed DEM', show: 'bool' = False, block: 'bool' = True)`
- Returns: `Any`
- Parameter `dem`: np.ndarray
- Parameter `save_path`: str | Path | None
- Parameter `title`: str
- Parameter `show`: bool
- Parameter `block`: bool
- Example:
```python
from lunadem import plot_depth_map
result = plot_depth_map(...)
print(result)
```

### 60. `plot_landing_site_2d`

- Purpose: Plot a 2D landing-site overlay with Plotly, Matplotlib, or both.
- Import: `from lunadem import plot_landing_site_2d`
- Signature: `plot_landing_site_2d(image_or_surface, landing_result, *, backend: 'PlotBackend' = 'plotly', show: 'bool' = False, save_path: 'str | Path | None' = None, html_path: 'str | Path | None' = None, block: 'bool' = True, title: 'str' = 'Safe Landing Site')`
- Returns: `Any`
- Parameter `image_or_surface`: Any
- Parameter `landing_result`: Any
- Parameter `backend`: PlotBackend
- Parameter `show`: bool
- Parameter `save_path`: str | Path | None
- Parameter `html_path`: str | Path | None
- Parameter `block`: bool
- Parameter `title`: str
- Example:
```python
from lunadem import find_safe_landing_site, plot_landing_site_2d, load_kaguya_scene
scene = load_kaguya_scene('TC1S2B0_01_07496N087E3020')
landing = find_safe_landing_site(scene.image_path, scene=scene)
plot_landing_site_2d(scene.image_path, landing, backend='both', show=False, save_path='output/landing_2d.png', html_path='output/landing_2d.html')
```

### 61. `plot_landing_site_3d`

- Purpose: Plot a 3D landing-site visualization with Plotly, Matplotlib, or both.
- Import: `from lunadem import plot_landing_site_3d`
- Signature: `plot_landing_site_3d(surface_or_dem, landing_result, *, backend: 'PlotBackend' = 'plotly', show: 'bool' = False, save_path: 'str | Path | None' = None, html_path: 'str | Path | None' = None, block: 'bool' = True, title: 'str' = '3D Landing Site Visualization')`
- Returns: `Any`
- Parameter `surface_or_dem`: Any
- Parameter `landing_result`: Any
- Parameter `backend`: PlotBackend
- Parameter `show`: bool
- Parameter `save_path`: str | Path | None
- Parameter `html_path`: str | Path | None
- Parameter `block`: bool
- Parameter `title`: str
- Example:
```python
from lunadem import find_safe_landing_site, plot_landing_site_3d, load_kaguya_scene
scene = load_kaguya_scene('TC1S2B0_01_07496N087E3020')
landing = find_safe_landing_site(scene.image_path, scene=scene)
plot_landing_site_3d(scene.image_path, landing, backend='both', show=False, save_path='output/landing_3d.png', html_path='output/landing_3d.html')
```

### 62. `plot_moon_surface_3d`

- Purpose: Plot the Moon globe, scene footprint, and space geometry.
- Import: `from lunadem import plot_moon_surface_3d`
- Signature: `plot_moon_surface_3d(scene, *, backend: 'PlotBackend' = 'plotly', show: 'bool' = False, save_path: 'str | Path | None' = None, html_path: 'str | Path | None' = None, block: 'bool' = True, title: 'str' = 'Moon Surface And Scene Geometry')`
- Returns: `Any`
- Parameter `scene`: Any
- Parameter `backend`: PlotBackend
- Parameter `show`: bool
- Parameter `save_path`: str | Path | None
- Parameter `html_path`: str | Path | None
- Parameter `block`: bool
- Parameter `title`: str
- Example:
```python
from lunadem import load_kaguya_scene, plot_moon_surface_3d
scene = load_kaguya_scene('TC1S2B0_01_07496N087E3020')
figure = plot_moon_surface_3d(scene, backend='both', show=False, save_path='output/moon_surface.png', html_path='output/moon_surface.html')
print(type(figure).__name__)
```

### 63. `plot_scene_geometry_3d`

- Purpose: Plot Moon/scene geometry with Plotly, Matplotlib, or both.
- Import: `from lunadem import plot_scene_geometry_3d`
- Signature: `plot_scene_geometry_3d(scene, *, backend: 'PlotBackend' = 'plotly', show: 'bool' = False, save_path: 'str | Path | None' = None, html_path: 'str | Path | None' = None, block: 'bool' = True, title: 'str' = 'Moon, Footprint, Camera, Sun, and Earth')`
- Returns: `Any`
- Parameter `scene`: Any
- Parameter `backend`: PlotBackend
- Parameter `show`: bool
- Parameter `save_path`: str | Path | None
- Parameter `html_path`: str | Path | None
- Parameter `block`: bool
- Parameter `title`: str
- Example:
```python
from lunadem import load_kaguya_scene, plot_scene_geometry_3d
scene = load_kaguya_scene('TC1S2B0_01_07496N087E3020')
figure = plot_scene_geometry_3d(scene, backend='both', show=False, save_path='output/scene_geometry.png', html_path='output/scene_geometry.html')
print(type(figure).__name__)
```

### 64. `predict_illumination`

- Purpose: Predict sun azimuth and sun elevation from an image or TIFF.
- Import: `from lunadem import predict_illumination`
- Signature: `predict_illumination(image_or_tif: 'np.ndarray | str | Path', *, max_patches: 'int' = 16) -> 'MetadataPrediction'`
- Returns: `MetadataPrediction`
- Parameter `image_or_tif`: np.ndarray | str | Path
- Parameter `max_patches`: int
- Example:
```python
from lunadem import predict_illumination
result = predict_illumination(...)
print(result)
```

### 65. `predict_scene_location`

- Purpose: Predict GSD and approximate scene centroid location from an image or TIFF.
- Import: `from lunadem import predict_scene_location`
- Signature: `predict_scene_location(image_or_tif: 'np.ndarray | str | Path', *, max_patches: 'int' = 16) -> 'MetadataPrediction'`
- Returns: `MetadataPrediction`
- Parameter `image_or_tif`: np.ndarray | str | Path
- Parameter `max_patches`: int
- Example:
```python
from lunadem import predict_scene_location
result = predict_scene_location(...)
print(result)
```

### 66. `predict_scene_metadata`

- Purpose: Run all bundled metadata models and return a merged prediction payload.
- Import: `from lunadem import predict_scene_metadata`
- Signature: `predict_scene_metadata(image_or_tif: 'np.ndarray | str | Path', *, max_patches: 'int' = 16) -> 'MetadataPrediction'`
- Returns: `MetadataPrediction`
- Parameter `image_or_tif`: np.ndarray | str | Path
- Parameter `max_patches`: int
- Example:
```python
from lunadem import predict_scene_metadata
prediction = predict_scene_metadata('dataset/TC1S2B0_01_07496N087E3020/image/image.tif', max_patches=8)
print(prediction.targets)
print(prediction.patch_count)
```

### 67. `predict_view_geometry`

- Purpose: Predict camera view azimuth and off-nadir angle from an image or TIFF.
- Import: `from lunadem import predict_view_geometry`
- Signature: `predict_view_geometry(image_or_tif: 'np.ndarray | str | Path', *, max_patches: 'int' = 16) -> 'MetadataPrediction'`
- Returns: `MetadataPrediction`
- Parameter `image_or_tif`: np.ndarray | str | Path
- Parameter `max_patches`: int
- Example:
```python
from lunadem import predict_view_geometry
result = predict_view_geometry(...)
print(result)
```

### 68. `projected_to_pixel`

- Purpose: Map projected coordinates back to pixel coordinates using a GDAL transform.
- Import: `from lunadem import projected_to_pixel`
- Signature: `projected_to_pixel(x: 'float', y: 'float', transform: 'Sequence[float]') -> 'Tuple[float, float]'`
- Returns: `Tuple[float, float]`
- Parameter `x`: float
- Parameter `y`: float
- Parameter `transform`: Sequence[float]
- Example:
```python
from lunadem import projected_to_pixel
result = projected_to_pixel(...)
print(result)
```

### 69. `rad_to_deg`

- Purpose: Convert radians to degrees.
- Import: `from lunadem import rad_to_deg`
- Signature: `rad_to_deg(value_rad: 'float') -> 'float'`
- Returns: `float`
- Parameter `value_rad`: float
- Example:
```python
from lunadem import rad_to_deg
result = rad_to_deg(...)
print(result)
```

### 70. `save_dem_as_geotiff`

- Purpose: Save DEM as a compressed GeoTIFF.
- Import: `from lunadem import save_dem_as_geotiff`
- Signature: `save_dem_as_geotiff(path: 'str | Path', dem: 'np.ndarray', georef: 'GeoreferenceConfig', metadata: 'Dict[str, Any] | None' = None) -> 'str'`
- Returns: `str`
- Parameter `path`: str | Path
- Parameter `dem`: np.ndarray
- Parameter `georef`: GeoreferenceConfig
- Parameter `metadata`: Dict[str, Any] | None
- Example:
```python
from lunadem import save_dem_as_geotiff
result = save_dem_as_geotiff(...)
print(result)
```

### 71. `save_dem_as_obj`

- Purpose: Save DEM as a Wavefront OBJ mesh.
- Import: `from lunadem import save_dem_as_obj`
- Signature: `save_dem_as_obj(path: 'str | Path', dem: 'np.ndarray') -> 'str'`
- Returns: `str`
- Parameter `path`: str | Path
- Parameter `dem`: np.ndarray
- Example:
```python
from lunadem import save_dem_as_obj
result = save_dem_as_obj(...)
print(result)
```

### 72. `save_dem_as_ply`

- Purpose: Save DEM as ASCII PLY mesh.
- Import: `from lunadem import save_dem_as_ply`
- Signature: `save_dem_as_ply(path: 'str | Path', dem: 'np.ndarray') -> 'str'`
- Returns: `str`
- Parameter `path`: str | Path
- Parameter `dem`: np.ndarray
- Example:
```python
from lunadem import save_dem_as_ply
result = save_dem_as_ply(...)
print(result)
```

### 73. `save_manifest`

- Purpose: Save manifest JSON for reproducibility.
- Import: `from lunadem import save_manifest`
- Signature: `save_manifest(path: 'str | Path', payload: 'Dict[str, Any]') -> 'str'`
- Returns: `str`
- Parameter `path`: str | Path
- Parameter `payload`: Dict[str, Any]
- Example:
```python
from lunadem import save_manifest
result = save_manifest(...)
print(result)
```

### 74. `scale_dem_to_meters`

- Purpose: Scale relative DEM to metric units.
- Import: `from lunadem import scale_dem_to_meters`
- Signature: `scale_dem_to_meters(dem: 'np.ndarray', sensor: 'SensorConfig', center: 'bool' = True) -> 'np.ndarray'`
- Returns: `np.ndarray`
- Parameter `dem`: np.ndarray
- Parameter `sensor`: SensorConfig
- Parameter `center`: bool
- Example:
```python
from lunadem import scale_dem_to_meters
result = scale_dem_to_meters(...)
print(result)
```

### 75. `scene_geometry_to_dict`

- Purpose: Convert a scene geometry object into a JSON-ready dictionary.
- Import: `from lunadem import scene_geometry_to_dict`
- Signature: `scene_geometry_to_dict(geometry: 'SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path') -> 'Dict[str, Any]'`
- Returns: `Dict[str, Any]`
- Parameter `geometry`: SceneGeometry | KaguyaScene | Mapping[str, Any] | str | Path
- Example:
```python
from lunadem import scene_geometry_to_dict
result = scene_geometry_to_dict(...)
print(result)
```

### 76. `show_depth_map`

- Purpose: Show a 2D terrain map using Matplotlib.
- Import: `from lunadem import show_depth_map`
- Signature: `show_depth_map(dem: 'np.ndarray', save_path: 'str | Path | None' = None, *, title: 'str' = 'Reconstructed DEM', block: 'bool' = True)`
- Returns: `Any`
- Parameter `dem`: np.ndarray
- Parameter `save_path`: str | Path | None
- Parameter `title`: str
- Parameter `block`: bool
- Example:
```python
from lunadem import show_depth_map
result = show_depth_map(...)
print(result)
```

### 77. `show_landing_site_2d`

- Purpose: Show a 2D landing-site overlay.
- Import: `from lunadem import show_landing_site_2d`
- Signature: `show_landing_site_2d(image_or_surface, landing_result, *, backend: 'PlotBackend' = 'matplotlib', save_path: 'str | Path | None' = None, html_path: 'str | Path | None' = None, block: 'bool' = True, title: 'str' = 'Safe Landing Site')`
- Returns: `Any`
- Parameter `image_or_surface`: Any
- Parameter `landing_result`: Any
- Parameter `backend`: PlotBackend
- Parameter `save_path`: str | Path | None
- Parameter `html_path`: str | Path | None
- Parameter `block`: bool
- Parameter `title`: str
- Example:
```python
from lunadem import show_landing_site_2d
result = show_landing_site_2d(...)
print(result)
```

### 78. `show_landing_site_3d`

- Purpose: Show a 3D landing-site visualization.
- Import: `from lunadem import show_landing_site_3d`
- Signature: `show_landing_site_3d(surface_or_dem, landing_result, *, backend: 'PlotBackend' = 'matplotlib', save_path: 'str | Path | None' = None, html_path: 'str | Path | None' = None, block: 'bool' = True, title: 'str' = '3D Landing Site Visualization')`
- Returns: `Any`
- Parameter `surface_or_dem`: Any
- Parameter `landing_result`: Any
- Parameter `backend`: PlotBackend
- Parameter `save_path`: str | Path | None
- Parameter `html_path`: str | Path | None
- Parameter `block`: bool
- Parameter `title`: str
- Example:
```python
from lunadem import show_landing_site_3d
result = show_landing_site_3d(...)
print(result)
```

### 79. `show_moon_surface_3d`

- Purpose: Show the Moon globe and scene footprint.
- Import: `from lunadem import show_moon_surface_3d`
- Signature: `show_moon_surface_3d(scene, *, backend: 'PlotBackend' = 'matplotlib', save_path: 'str | Path | None' = None, html_path: 'str | Path | None' = None, block: 'bool' = True, title: 'str' = 'Moon Surface And Scene Geometry')`
- Returns: `Any`
- Parameter `scene`: Any
- Parameter `backend`: PlotBackend
- Parameter `save_path`: str | Path | None
- Parameter `html_path`: str | Path | None
- Parameter `block`: bool
- Parameter `title`: str
- Example:
```python
from lunadem import show_moon_surface_3d
result = show_moon_surface_3d(...)
print(result)
```

### 80. `show_scene_geometry_3d`

- Purpose: Show Moon/scene geometry.
- Import: `from lunadem import show_scene_geometry_3d`
- Signature: `show_scene_geometry_3d(scene, *, backend: 'PlotBackend' = 'matplotlib', save_path: 'str | Path | None' = None, html_path: 'str | Path | None' = None, block: 'bool' = True, title: 'str' = 'Moon, Footprint, Camera, Sun, and Earth')`
- Returns: `Any`
- Parameter `scene`: Any
- Parameter `backend`: PlotBackend
- Parameter `save_path`: str | Path | None
- Parameter `html_path`: str | Path | None
- Parameter `block`: bool
- Parameter `title`: str
- Example:
```python
from lunadem import show_scene_geometry_3d
result = show_scene_geometry_3d(...)
print(result)
```

### 81. `show_surface_3d`

- Purpose: Show a 3D terrain surface using Matplotlib.
- Import: `from lunadem import show_surface_3d`
- Signature: `show_surface_3d(dem: 'np.ndarray', save_path: 'str | Path | None' = None, *, title: 'str' = 'Reconstructed 3D Surface', block: 'bool' = True, max_points: 'int' = 200)`
- Returns: `Any`
- Parameter `dem`: np.ndarray
- Parameter `save_path`: str | Path | None
- Parameter `title`: str
- Parameter `block`: bool
- Parameter `max_points`: int
- Example:
```python
from lunadem import show_surface_3d
result = show_surface_3d(...)
print(result)
```

### 82. `summarize_scene_metadata`

- Purpose: Derive scene geometry from STAC and camera-model metadata.
- Import: `from lunadem import summarize_scene_metadata`
- Signature: `summarize_scene_metadata(item: 'Mapping[str, Any] | str | Path', camera_model: 'Mapping[str, Any] | str | Path | None' = None) -> 'SceneGeometry'`
- Returns: `SceneGeometry`
- Parameter `item`: Mapping[str, Any] | str | Path
- Parameter `camera_model`: Mapping[str, Any] | str | Path | None
- Example:
```python
from lunadem import summarize_scene_metadata
result = summarize_scene_metadata(...)
print(result)
```

## Notes

- Plotting functions support desktop-visible Matplotlib rendering, hoverable Plotly output, or both.
- Metadata prediction functions use bundled ONNX weights and run offline after installation.
- `lunardem` remains import-compatible, but new code should use `lunadem` everywhere.
