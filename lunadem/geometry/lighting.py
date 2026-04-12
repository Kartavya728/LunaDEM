"""Lighting geometry transformations."""

from __future__ import annotations

import numpy as np

from lunadem.native import native_compute_light_vector


def get_light_vector(sun_azimuth_deg: float, sun_elevation_deg: float) -> np.ndarray:
    """Convert sun azimuth/elevation to a unit light vector.

    Coordinate system: +X east, +Y north, +Z up.
    Azimuth is measured clockwise from north.
    """
    if native_compute_light_vector is not None:
        return np.asarray(native_compute_light_vector(sun_azimuth_deg, sun_elevation_deg), dtype=np.float64)

    az_rad = np.deg2rad(sun_azimuth_deg)
    el_rad = np.deg2rad(sun_elevation_deg)

    z = np.sin(el_rad)
    xy_proj = np.cos(el_rad)
    x = xy_proj * np.sin(az_rad)
    y = xy_proj * np.cos(az_rad)

    vec = np.array([x, y, z], dtype=np.float64)
    norm = np.linalg.norm(vec)
    if norm <= 0:
        raise ValueError("Invalid light vector norm; check illumination angles.")
    return vec / norm
