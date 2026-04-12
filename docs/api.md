# API Reference

## Main functions

- `lunadem.generate_dem(input_data, method="sfs", config=None, analysis_config=None)`
- `lunadem.analyze_dem(dem_or_path, analysis_config=None)`
- `lunadem.assess_landing(dem_or_path, landing_config=None, analysis_config=None)`
- `lunadem.load_stac_item(scene_id_or_path)`
- `lunadem.load_camera_model(scene_id_or_path)`
- `lunadem.load_kaguya_scene(scene_id_or_path)`
- `lunadem.summarize_scene_metadata(item, camera_model)`
- `lunadem.predict_scene_metadata(image_or_tif)`
- `lunadem.find_safe_landing_site(image_or_dem, rover=..., scene=...)`

## Configuration models

- `ReconstructionConfig`
- `AnalysisConfig`
- `LandingConfig`

## Result models

- `DEMResult`
- `TerrainMetrics`
- `LandingReport`
- `SceneGeometry`
- `KaguyaScene`
- `MetadataPrediction`
- `RoverSpec`
- `LandingSiteResult`
