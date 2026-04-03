"""Filesystem helpers."""

from __future__ import annotations

from pathlib import Path


def ensure_directory(path: str | Path) -> Path:
    """Create a directory when missing and return it as a Path."""
    out = Path(path)
    out.mkdir(parents=True, exist_ok=True)
    return out
