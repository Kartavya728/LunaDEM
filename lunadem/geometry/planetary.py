"""Planetary coordinate constants and helpers."""

from __future__ import annotations

MOON_RADIUS_M = 1_737_400.0

# Spherical Moon CRS using radius from IAU lunar body parameters.
DEFAULT_MOON_CRS = "+proj=longlat +a=1737400 +b=1737400 +no_defs"

