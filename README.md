# lunadem

`lunadem` is a lunar analysis toolkit for shape-from-shading DEM reconstruction, Kaguya scene metadata parsing, packaged metadata prediction, rover-aware landing safety scoring, and interactive 3D visualization.

PyPI: https://pypi.org/project/lunadem/

## Install

```bash
pip install lunadem
```

Optional extras:

```bash
pip install "lunadem[ml]"
pip install "lunadem[viz]"
pip install "lunadem[pds]"
pip install "lunadem[dev]"
```

Canonical Python import is now `lunadem`.

Backward compatibility:

- `import lunardem` still works, but it is deprecated.
- `lunardem` remains available as a compatibility CLI alias.

## What It Includes

- DEM generation from image input with `sfs`, `multiscale_sfs`, `ml`, and `hybrid`
- STAC + `camera.json` loaders for the bundled Kaguya dataset
- Deterministic metadata derivation helpers for geometry, timing, coverage, and coordinate conversion
- Packaged SFS explainers via CLI and Python
- Packaged metadata prediction APIs with ONNX-ready runtime hooks and baseline fallback metadata priors
- Rover preset library for Sojourner, Spirit, Opportunity, Curiosity, Perseverance, Pragyan, and SORA-Q
- Safe landing-site selection from an image or DEM
- Interactive Plotly visualizations for surfaces, landing sites, and Moon/footprint/camera/sun geometry
- `download --test` to fetch the official reference scene

## Quick Start

```python
from lunadem import (
    ReconstructionConfig,
    find_safe_landing_site,
    generate_dem,
    load_kaguya_scene,
    predict_scene_metadata,
    plot_scene_geometry_3d,
)

scene = load_kaguya_scene("TC1S2B0_01_07496N087E3020")

cfg = ReconstructionConfig(
    output={"output_dir": "output", "base_name": "moon_run"},
)
dem_result = generate_dem(scene.image_path, method="hybrid", config=cfg)

metadata_prediction = predict_scene_metadata(scene.image_path)
landing_site = find_safe_landing_site(scene.image_path, rover="pragyan", scene=scene)

figure = plot_scene_geometry_3d(scene, save_path="output/scene_geometry.html")

print(dem_result.exports)
print(metadata_prediction.targets)
print(landing_site.summary)
```

## CLI Examples

```bash
lunadem generate dataset/TC1S2B0_01_07496N087E3020/image/image.tif --method hybrid --output output
lunadem scene-summary TC1S2B0_01_07496N087E3020
lunadem sfs --maths
lunadem predict dataset/TC1S2B0_01_07496N087E3020/image/image.tif --kind all
lunadem landing-site dataset/TC1S2B0_01_07496N087E3020/image/image.tif --rover pragyan --scene TC1S2B0_01_07496N087E3020
lunadem download --test --output downloads
```

## Metadata Suite Accuracy

The bundled 18-scene Kaguya metadata suite currently ships baseline packaged statistics and ONNX-ready runtime hooks. The table below shows mean absolute error against the local dataset targets used by the packaged metrics file.

| Target | MAE |
| --- | ---: |
| `sun_azimuth_deg` | 1.5308 |
| `sun_elevation_deg` | 0.0022 |
| `off_nadir_deg` | 0.1052 |
| `view_azimuth_deg` | 0.0513 |
| `gsd_m` | 0.0808 |
| `centroid_lat_deg` | 3.0003 |
| `centroid_lon_deg` | 0.5092 |

Important note:

- The current dataset is small and scene-level labels are limited.
- These predictors estimate scene metadata, not ground-truth DEM quality or landing safety labels.
- Running `tools/train_metadata_cnns.py` in a healthy Python environment will replace the packaged baseline with exported ONNX models and refreshed metrics.

## Main Public APIs

- `generate_dem(...)`
- `analyze_dem(...)`
- `assess_landing(...)`
- `load_stac_item(...)`
- `load_camera_model(...)`
- `load_kaguya_scene(...)`
- `summarize_scene_metadata(...)`
- `predict_illumination(...)`
- `predict_view_geometry(...)`
- `predict_scene_location(...)`
- `predict_scene_metadata(...)`
- `get_rover_spec(...)`
- `find_safe_landing_site(...)`
- `plot_3d_surface_interactive(...)`
- `plot_landing_site_2d(...)`
- `plot_landing_site_3d(...)`
- `plot_scene_geometry_3d(...)`

## Reference Files

- [sfs.md](sfs.md)
- [lunar_data.md](lunar_data.md)
- [run.md](run.md)
- [update.md](update.md)

## License

MIT License. See [LICENSE](LICENSE).
