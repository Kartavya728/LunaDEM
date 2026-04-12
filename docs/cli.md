# CLI Usage

The canonical CLI is `lunadem`.

Compatibility alias:

- `lunardem` still works, but it is deprecated.

## DEM generation

```bash
lunadem generate input.png --method hybrid --output output
lunadem analyze output/reconstructed_dem.tif
lunadem landing output/reconstructed_dem.tif --spacecraft config.yaml
```

## SFS explainers

```bash
lunadem sfs --maths
lunadem sfs --terms
lunadem sfs --assumptions
```

## Scene and metadata tools

```bash
lunadem scene-summary TC1S2B0_01_07496N087E3020
lunadem predict dataset/TC1S2B0_01_07496N087E3020/image/image.tif --kind all
lunadem download --test --output downloads
```

## Rover landing tools

```bash
lunadem landing-site dataset/TC1S2B0_01_07496N087E3020/image/image.tif --scene TC1S2B0_01_07496N087E3020 --rover pragyan
lunadem plot-scene TC1S2B0_01_07496N087E3020 --output-html output/scene_geometry.html
```

## Config file support

Core DEM commands accept JSON or YAML config files where applicable.
