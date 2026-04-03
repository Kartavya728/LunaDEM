# API Reference

## Main functions

- `lunardem.generate_dem(input_data, method="sfs", config=None, analysis_config=None)`
- `lunardem.analyze_dem(dem_or_path, analysis_config=None)`
- `lunardem.assess_landing(dem_or_path, landing_config=None, analysis_config=None)`

## Configuration models

- `ReconstructionConfig`
- `AnalysisConfig`
- `LandingConfig`

## Result models

- `DEMResult`
- `TerrainMetrics`
- `LandingReport`
