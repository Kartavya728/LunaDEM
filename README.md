# lunadem

`lunadem` is a lunar terrain analysis library for DEM reconstruction, Kaguya scene metadata understanding, offline metadata prediction, rover-aware landing analysis, and dual-backend visualization.

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

Canonical import and CLI name is `lunadem`.

Compatibility note:

- `import lunardem` still works as a deprecated compatibility shim.
- `lunardem` still exists as a compatibility CLI alias.

## Main Capabilities

- DEM generation from images with `sfs`, `multiscale_sfs`, `ml`, and `hybrid` methods.
- Memory-safe SFS and hybrid reconstruction for large Kaguya scenes through bounded working resolution.
- Kaguya scene loading from STAC `item.json` plus `camera.json`.
- Dozens of deterministic metadata helpers for centroid, bbox, footprint, coverage, transforms, angles, camera path, and sun geometry.
- Packaged shape-from-shading theory helpers through CLI and Python.
- Packaged offline ONNX metadata models for illumination, view geometry, and scene context prediction.
- Rover presets for `sojourner`, `spirit`, `opportunity`, `curiosity`, `perseverance`, `pragyan`, and `soraq`.
- Rover-aware landing-site search using slope, roughness, hazard, clearance, and optional sun geometry.
- Matplotlib plotting for visible local rendering and Plotly for hoverable 3D output and HTML export.
- Moon-globe, terrain-surface, landing-site, and scene-geometry visualization.
- `download --test` support for the official reference scene.

## Bundled Resources

- Kaguya dataset access helpers in `lunadem.datasets`.
- SFS theory files in `lunadem/assets/docs/`.
- Real packaged ONNX model weights in `lunadem/assets/models/`.
- Packaged metrics file describing the current model suite.
- Rover preset catalog in `lunadem.landing.rovers`.
- Optional C++ acceleration hook under `lunadem._native` when built with native support.
- Detailed generated references in [run.md](run.md), [lunar_data.md](lunar_data.md), [sfs.md](sfs.md), [documentation.txt](documentation.txt), and [update.md](update.md).

## Quick Start

```python
from lunadem import (
    ReconstructionConfig,
    build_scene_summary,
    find_safe_landing_site,
    generate_dem,
    get_rover_spec,
    load_kaguya_scene,
    plot_landing_site_2d,
    plot_moon_surface_3d,
    plot_scene_geometry_3d,
    predict_scene_metadata,
)

scene = load_kaguya_scene("TC1S2B0_01_07496N087E3020")
summary = build_scene_summary(scene)

config = ReconstructionConfig(
    output={"output_dir": "output", "base_name": "moon_demo"},
)

dem_result = generate_dem(scene.image_path, method="hybrid", config=config)
prediction = predict_scene_metadata(scene.image_path, max_patches=8)
landing = find_safe_landing_site(scene.image_path, rover=get_rover_spec("pragyan"), scene=scene)

plot_scene_geometry_3d(
    scene,
    backend="both",
    show=False,
    save_path="output/scene_geometry.png",
    html_path="output/scene_geometry.html",
)
plot_moon_surface_3d(
    scene,
    backend="both",
    show=False,
    save_path="output/moon_surface.png",
    html_path="output/moon_surface.html",
)
plot_landing_site_2d(
    scene.image_path,
    landing,
    backend="both",
    show=False,
    save_path="output/landing_2d.png",
    html_path="output/landing_2d.html",
)

print(summary["centroid"])
print(prediction.targets)
print(landing.summary)
```

## CLI Overview

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

## Plotting Backends

- Use Matplotlib when you want visible local plots or static PNG output.
- Use Plotly when you want hoverable 3D interaction or HTML export.
- Use `backend="both"` for the scene, Moon, and landing plot helpers when you want both at once.
- Python plotting APIs default to `show=False` so scripts stay safe.
- CLI plot commands default to `--show`, which makes desktop visualization available immediately.

## Public API Scope

The current public package surface exposes more than 40 callable functions and helper APIs across:

- DEM generation and terrain analysis.
- Scene loading and metadata derivation.
- Coordinate and unit conversion.
- Metadata model inspection and prediction.
- Rover preset lookup and landing-site selection.
- Matplotlib and Plotly visualization helpers.
- File export helpers for GeoTIFF, OBJ, PLY, and manifest generation.

Full callable catalog and examples are in [run.md](run.md).

The long-form generated manual with parameter breakdowns and code templates is in [documentation.txt](documentation.txt).

## Packaged Model Metrics

The current wheel bundles real ONNX artifacts for the metadata suite. The metrics below come from grouped scene-level evaluation on the local 18-scene Kaguya dataset.

| Model | Target | MAE |
| --- | --- | ---: |
| `illumination_cnn` | `sun_azimuth_deg` | 1.608062 |
| `illumination_cnn` | `sun_elevation_deg` | 0.002216 |
| `view_geometry_cnn` | `off_nadir_deg` | 0.105210 |
| `view_geometry_cnn` | `view_azimuth_deg` | 0.051268 |
| `scene_context_cnn` | `gsd_m` | 0.082854 |
| `scene_context_cnn` | `centroid_lat_deg` | 3.149079 |
| `scene_context_cnn` | `centroid_lon_deg` | 0.509205 |

Important note:

- These models estimate scene metadata from imagery.
- They are not trained as ground-truth DEM regressors.
- They are not trained as supervised landing-safety classifiers.
- The local dataset is still small, so accuracy should be treated as a practical estimate rather than a broad benchmark.

## Reference Files

- [run.md](run.md): generated command and Python function catalog with examples.
- [documentation.txt](documentation.txt): long-form generated manual exceeding 2000 lines.
- [lunar_data.md](lunar_data.md): explanation of the Kaguya STAC and camera metadata concepts used by the library.
- [sfs.md](sfs.md): shape-from-shading concepts, mathematics, terms, and assumptions.
- [update.md](update.md): GitHub and PyPI release workflow.

## Development Notes

- The package version is sourced from `lunadem/__init__.py`.
- Native acceleration is optional and every accelerated path has a Python fallback.
- The ONNX model artifacts are bundled inside the package, so end users do not need to download weights separately.
- The official reference scene remains `TC1S2B0_01_07496N087E3020`.

## License

MIT License. See [LICENSE](LICENSE).
