"""Minimal PDS label adapters for extensible planetary ingestion."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def _parse_simple_lbl(text: str) -> Dict[str, Any]:
    parsed: Dict[str, Any] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("/*"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"')
        parsed[key] = value
    return parsed


def load_pds_label(path: str | Path) -> Dict[str, Any]:
    """Load PDS label with optional `pvl` backend and fallback parser."""
    label_path = Path(path)
    if not label_path.exists():
        raise FileNotFoundError(f"PDS label not found: {label_path}")

    try:
        import pvl  # type: ignore

        parsed = pvl.load(str(label_path))
        if hasattr(parsed, "as_dict"):
            return parsed.as_dict()
        return dict(parsed)
    except Exception:
        return _parse_simple_lbl(label_path.read_text(encoding="utf-8", errors="ignore"))


def extract_pds_geometry(label: Dict[str, Any]) -> Dict[str, Any]:
    """Extract common geometry fields from parsed label dictionary."""
    keys = [
        "CENTER_LATITUDE",
        "CENTER_LONGITUDE",
        "SUB_SOLAR_AZIMUTH",
        "INCIDENCE_ANGLE",
        "EMISSION_ANGLE",
        "PHASE_ANGLE",
    ]
    return {key: label.get(key) for key in keys if key in label}
