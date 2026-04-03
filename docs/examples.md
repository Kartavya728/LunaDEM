# Examples

## Python

```python
from lunardem import ReconstructionConfig, generate_dem

cfg = ReconstructionConfig(output={"output_dir": "output", "base_name": "demo"})
result = generate_dem("data/moon1.png", method="multiscale_sfs", config=cfg)
print(result.exports)
```

## CLI + YAML

```bash
lunardem generate data/moon1.png --method hybrid --config examples/configs/reconstruction.yaml
```

## Legacy web demo

A minimal Flask demo is available at `examples/webapp/app.py`.
