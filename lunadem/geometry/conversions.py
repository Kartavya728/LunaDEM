"""Unit and coordinate conversions for lunar geometry workflows."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, Sequence, Tuple

import numpy as np

from lunadem.geometry.planetary import MOON_RADIUS_M


def deg_to_rad(value_deg: float) -> float:
    """Convert degrees to radians."""
    return float(np.deg2rad(value_deg))


def rad_to_deg(value_rad: float) -> float:
    """Convert radians to degrees."""
    return float(np.rad2deg(value_rad))


def km_to_m(value_km: float) -> float:
    """Convert kilometers to meters."""
    return float(value_km * 1_000.0)


def m_to_km(value_m: float) -> float:
    """Convert meters to kilometers."""
    return float(value_m / 1_000.0)


def mm_to_m(value_mm: float) -> float:
    """Convert millimeters to meters."""
    return float(value_mm / 1_000.0)


def m_to_mm(value_m: float) -> float:
    """Convert meters to millimeters."""
    return float(value_m * 1_000.0)


def acquisition_duration_seconds(start_datetime: str, end_datetime: str) -> float:
    """Compute acquisition duration in seconds from ISO timestamps."""
    start = datetime.fromisoformat(start_datetime.replace("Z", "+00:00"))
    end = datetime.fromisoformat(end_datetime.replace("Z", "+00:00"))
    return float((end - start).total_seconds())


def line_time_seconds(duration_s: float, image_lines: int) -> float:
    """Compute approximate line scan time from duration and line count."""
    if image_lines <= 0:
        raise ValueError("image_lines must be positive.")
    return float(duration_s / image_lines)


def ground_coverage_meters(shape: Sequence[int], gsd_m: float) -> Tuple[float, float]:
    """Return ground height/width in meters for an image shape and GSD."""
    rows, cols = int(shape[0]), int(shape[1])
    return float(rows * gsd_m), float(cols * gsd_m)


def bbox_area_deg2(bbox: Sequence[float]) -> float:
    """Approximate angular area of a lon/lat bbox in square degrees."""
    min_lon, min_lat, max_lon, max_lat = [float(x) for x in bbox]
    return float(abs(max_lon - min_lon) * abs(max_lat - min_lat))


def bbox_area_km2(bbox: Sequence[float], lat_center_deg: float, radius_m: float = MOON_RADIUS_M) -> float:
    """Approximate lunar surface area of a lon/lat bbox in square kilometers."""
    min_lon, min_lat, max_lon, max_lat = [float(x) for x in bbox]
    dlon = np.deg2rad(abs(max_lon - min_lon))
    dlat = np.deg2rad(abs(max_lat - min_lat))
    lat_scale = np.cos(np.deg2rad(lat_center_deg))
    width_m = radius_m * dlon * max(lat_scale, 1e-8)
    height_m = radius_m * dlat
    return float(width_m * height_m / 1_000_000.0)


def latlon_to_cartesian_moon(
    lat_deg: float,
    lon_deg: float,
    radius_m: float = MOON_RADIUS_M,
) -> Tuple[float, float, float]:
    """Convert lunar latitude/longitude to Cartesian coordinates."""
    lat = np.deg2rad(lat_deg)
    lon = np.deg2rad(lon_deg)
    x = radius_m * np.cos(lat) * np.cos(lon)
    y = radius_m * np.cos(lat) * np.sin(lon)
    z = radius_m * np.sin(lat)
    return float(x), float(y), float(z)


def cartesian_to_latlon_moon(
    x_m: float,
    y_m: float,
    z_m: float,
) -> Tuple[float, float, float]:
    """Convert Cartesian coordinates to lunar latitude/longitude and radius."""
    radius = float(np.sqrt(x_m**2 + y_m**2 + z_m**2))
    if radius <= 0:
        raise ValueError("Cartesian vector magnitude must be positive.")
    lat = float(np.rad2deg(np.arcsin(z_m / radius)))
    lon = float(np.rad2deg(np.arctan2(y_m, x_m)))
    return lat, lon, radius


def pixel_to_projected(row: float, col: float, transform: Sequence[float]) -> Tuple[float, float]:
    """Map pixel coordinates to projected coordinates using a GDAL transform."""
    if len(transform) < 6:
        raise ValueError("transform must contain at least 6 values.")
    x0, a, b, y0, d, e = [float(x) for x in transform[:6]]
    x = x0 + col * a + row * b
    y = y0 + col * d + row * e
    return float(x), float(y)


def projected_to_pixel(x: float, y: float, transform: Sequence[float]) -> Tuple[float, float]:
    """Map projected coordinates back to pixel coordinates using a GDAL transform."""
    if len(transform) < 6:
        raise ValueError("transform must contain at least 6 values.")
    x0, a, b, y0, d, e = [float(v) for v in transform[:6]]
    matrix = np.array([[a, b], [d, e]], dtype=np.float64)
    rhs = np.array([x - x0, y - y0], dtype=np.float64)
    row_col = np.linalg.solve(matrix, rhs)
    col, row = row_col.tolist()
    return float(row), float(col)


def mean_vector(values: Iterable[Sequence[float]]) -> np.ndarray | None:
    """Return the arithmetic mean vector for a collection of numeric sequences."""
    values_list = [np.asarray(value, dtype=np.float64) for value in values]
    if not values_list:
        return None
    return np.mean(np.stack(values_list, axis=0), axis=0)


def path_length(values: Iterable[Sequence[float]]) -> float:
    """Return the total Euclidean path length across sequential vectors."""
    values_list = [np.asarray(value, dtype=np.float64) for value in values]
    if len(values_list) < 2:
        return 0.0
    diffs = np.diff(np.stack(values_list, axis=0), axis=0)
    return float(np.sum(np.linalg.norm(diffs, axis=1)))
