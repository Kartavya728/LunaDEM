# Run Guide For lunadem

This file shows the main commands and Python calls using the official test scene `TC1S2B0_01_07496N087E3020`.

## 1. Download The Test Scene

```bash
lunadem download --test --output downloads
```

## 2. Explain Shape From Shading

```bash
lunadem sfs --maths
lunadem sfs --terms
lunadem sfs --assumptions
```

## 3. Summarize Scene Metadata

```bash
lunadem scene-summary TC1S2B0_01_07496N087E3020
```

## 4. Predict Metadata From The Image

```bash
lunadem predict dataset/TC1S2B0_01_07496N087E3020/image/image.tif --kind all
lunadem predict dataset/TC1S2B0_01_07496N087E3020/image/image.tif --kind illumination
lunadem predict dataset/TC1S2B0_01_07496N087E3020/image/image.tif --kind view
lunadem predict dataset/TC1S2B0_01_07496N087E3020/image/image.tif --kind location
```

## 5. Generate A DEM

```bash
lunadem generate dataset/TC1S2B0_01_07496N087E3020/image/image.tif --method hybrid --output output
```

## 6. Find The Safest Landing Site

```bash
lunadem landing-site dataset/TC1S2B0_01_07496N087E3020/image/image.tif --scene TC1S2B0_01_07496N087E3020 --rover pragyan --output-2d-html output/landing_2d.html --output-3d-html output/landing_3d.html
```

## 7. Plot Moon / Sun / Camera / Footprint Geometry

```bash
lunadem plot-scene TC1S2B0_01_07496N087E3020 --output-html output/scene_geometry.html
```

## 8. Standard Python Usage

```python
from lunadem import (
    find_safe_landing_site,
    generate_dem,
    get_model_metrics,
    get_rover_spec,
    load_camera_model,
    load_kaguya_scene,
    load_stac_item,
    plot_3d_surface_interactive,
    plot_landing_site_2d,
    plot_landing_site_3d,
    plot_scene_geometry_3d,
    predict_scene_metadata,
    summarize_scene_metadata,
)

scene = load_kaguya_scene("TC1S2B0_01_07496N087E3020")
item = load_stac_item(scene.item_path)
camera = load_camera_model(scene.camera_path)
geometry = summarize_scene_metadata(item, camera)

prediction = predict_scene_metadata(scene.image_path)
dem_result = generate_dem(scene.image_path, method="hybrid")
rover = get_rover_spec("pragyan")
landing_site = find_safe_landing_site(scene.image_path, rover=rover, scene=scene)

surface_figure = plot_3d_surface_interactive(dem_result.dem_meters, save_path="output/surface_interactive.html")
landing_2d = plot_landing_site_2d(scene.image_path, landing_site, save_path="output/landing_2d.html")
landing_3d = plot_landing_site_3d(dem_result.dem_meters, landing_site, save_path="output/landing_3d.html")
space_figure = plot_scene_geometry_3d(scene, save_path="output/scene_geometry.html")

print(geometry)
print(prediction.targets)
print(get_model_metrics())
print(landing_site.summary)
```

## 9. Useful Built-In Rover Names

- `sojourner`
- `spirit`
- `opportunity`
- `curiosity`
- `perseverance`
- `pragyan`
- `soraq`
