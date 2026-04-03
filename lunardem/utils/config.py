"""Configuration file loading helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import yaml


def load_config_file(path: str | Path) -> Dict[str, Any]:
    """Load JSON or YAML configuration into a dictionary."""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    suffix = config_path.suffix.lower()
    text = config_path.read_text(encoding="utf-8")

    if suffix in {".yaml", ".yml"}:
        data = yaml.safe_load(text)
    elif suffix == ".json":
        data = json.loads(text)
    else:
        raise ValueError(f"Unsupported config format: {suffix}")

    if not isinstance(data, dict):
        raise ValueError("Configuration file must contain a dictionary/object at the top level.")
    return data
