# LunarDEM

LunarDEM is a production-oriented Python library for generating and analyzing Digital Elevation Models (DEM) from lunar and planetary imagery.

It ships with:

- shape-from-shading (SFS) reconstruction
- multi-scale SFS
- plugin-ready ML method scaffolding
- hybrid SFS + ML fusion
- terrain analytics (slope, roughness, curvature, histograms)
- deterministic landing suitability analysis
- geospatial exports (GeoTIFF, OBJ, PLY)
- CLI + Python API + PyPI-ready packaging

## Installation

```bash
pip install .
```

Optional extras:

```bash
pip install .[viz]
pip install .[ml]
pip install .[docs]
pip install .[dev]
```

## Quick Start (Python API)

```python
from lunardem import generate_dem, ReconstructionConfig

config = ReconstructionConfig(
    output={"output_dir": "output", "base_name": "moon_run"},
)
result = generate_dem("data/moon1.png", method="multiscale_sfs", config=config)
print(result.exports)
print(result.metrics.stats)
```

## Quick Start (CLI)

```bash
lunardem generate data/moon1.png --method sfs --output output
lunardem analyze output/reconstructed_dem.tif
lunardem landing output/reconstructed_dem.tif --spacecraft examples/configs/landing.yaml
```

## Public API

- `generate_dem(input_data, method, config) -> DEMResult`
- `analyze_dem(dem_or_path, analysis_config) -> TerrainMetrics`
- `assess_landing(dem_or_path, landing_config) -> LandingReport`

## Methods

- `sfs`: single-scale Lambertian SFS with optimization diagnostics
- `multiscale_sfs`: coarse-to-fine SFS
- `ml`: deterministic baseline scaffold with optional torch plugin path
- `hybrid`: weighted SFS+ML fusion with fallback behavior

## Outputs

- DEM array in meters
- GeoTIFF (`.tif`) with planetary CRS defaults
- 3D mesh (`.obj`, optional `.ply`)
- Visualizations (`depth_map.png`, `surface_3d.png`) with `viz` extra
- JSON manifest for reproducibility

## Documentation

Build docs locally:

```bash
pip install .[docs]
mkdocs serve
```

## Development

```bash
pip install .[dev]
pytest
ruff check .
mypy lunardem
python -m build
twine check dist/*
```

## Publish to PyPI

```bash
python -m build
twine check dist/*
twine upload dist/*
```

## License

MIT License. See [LICENSE](LICENSE).
