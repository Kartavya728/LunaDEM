"""Run manifest serialization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def save_manifest(path: str | Path, payload: Dict[str, Any]) -> str:
    """Save manifest JSON for reproducibility."""
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return str(out_path)
