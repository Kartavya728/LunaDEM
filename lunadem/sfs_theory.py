"""Packaged SFS theory content for CLI and Python access."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path


def _read_doc(filename: str) -> str:
    path = Path(files("lunadem")).joinpath("assets", "docs", filename)
    return path.read_text(encoding="utf-8")


def get_sfs_math() -> str:
    """Return the packaged SFS mathematics document."""
    return _read_doc("sfs_maths.md")


def get_sfs_terms() -> str:
    """Return the packaged SFS terminology document."""
    return _read_doc("sfs_terms.md")


def get_sfs_assumptions() -> str:
    """Return the packaged SFS assumptions document."""
    return _read_doc("sfs_assumptions.md")
