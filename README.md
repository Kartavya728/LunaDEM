# lunadem

`lunadem` is a Python library for generating and analyzing Digital Elevation Models (DEM) from lunar and planetary images.

PyPI release page:

https://pypi.org/project/lunadem/0.1.1/

## Install

```bash
pip install lunadem
```

Note: in code, current module import is `lunardem`.

## Main Capabilities

- DEM generation from image input (PNG, JPG, TIFF, GeoTIFF)
- Multiple methods: `sfs`, `multiscale_sfs`, `ml`, `hybrid`
- Terrain analytics: slope, roughness, curvature, elevation statistics, histogram summaries
- Landing suitability: safe/unsafe masks, hazard filtering, score and safe-area summary
- Exports: GeoTIFF DEM, OBJ/PLY mesh, visualization images, JSON run manifest

## Core Functions (Python API)

- `generate_dem(input_data, method, config) -> DEMResult`
- `analyze_dem(dem_or_path, analysis_config) -> TerrainMetrics`
- `assess_landing(dem_or_path, landing_config) -> LandingReport`

## Quick API Example

```python
from lunardem import ReconstructionConfig, generate_dem

cfg = ReconstructionConfig(
    output={"output_dir": "output", "base_name": "moon_run"},
)
result = generate_dem("data/moon1.png", method="multiscale_sfs", config=cfg)
print(result.exports)
print(result.metrics.stats)
```

## CLI Usage

```bash
lunardem generate data/moon1.png --method sfs --output output
lunardem analyze output/reconstructed_dem.tif
lunardem landing output/reconstructed_dem.tif --spacecraft examples/configs/landing.yaml
```

## Web App Usage

Web app is provided as a demo in:

`examples/webapp/app.py`

Run:

```bash
python examples/webapp/app.py
```

Then open:

`http://127.0.0.1:5000/`

Endpoints:

- `GET /` health message
- `POST /generate` image upload + DEM generation response

## Optional Extras

```bash
pip install "lunadem[viz]"
pip install "lunadem[ml]"
pip install "lunadem[pds]"
pip install "lunadem[docs]"
pip install "lunadem[dev]"
```

## License

MIT License. See [LICENSE](LICENSE).
