# CLI Usage

## Generate DEM

```bash
lunardem generate input.png --method sfs --output output
```

## Analyze DEM

```bash
lunardem analyze output/reconstructed_dem.tif
```

## Landing suitability

```bash
lunardem landing output/reconstructed_dem.tif --spacecraft config.yaml
```

## Config file support

All CLI commands accept JSON or YAML config files where applicable.
