"""Geometry and planetary coordinate utilities."""

from lunadem.geometry.conversions import (
    acquisition_duration_seconds,
    bbox_area_deg2,
    bbox_area_km2,
    cartesian_to_latlon_moon,
    deg_to_rad,
    ground_coverage_meters,
    km_to_m,
    latlon_to_cartesian_moon,
    line_time_seconds,
    m_to_km,
    m_to_mm,
    mm_to_m,
    pixel_to_projected,
    projected_to_pixel,
    rad_to_deg,
)
from lunadem.geometry.lighting import get_light_vector
from lunadem.geometry.planetary import DEFAULT_MOON_CRS, MOON_RADIUS_M
from lunadem.geometry.scaling import pixel_scale_meters, scale_dem_to_meters
from lunadem.geometry.surface import calculate_predicted_image, calculate_surface_normals

__all__ = [
    "DEFAULT_MOON_CRS",
    "MOON_RADIUS_M",
    "acquisition_duration_seconds",
    "bbox_area_deg2",
    "bbox_area_km2",
    "calculate_predicted_image",
    "calculate_surface_normals",
    "cartesian_to_latlon_moon",
    "deg_to_rad",
    "get_light_vector",
    "ground_coverage_meters",
    "km_to_m",
    "latlon_to_cartesian_moon",
    "line_time_seconds",
    "m_to_km",
    "m_to_mm",
    "mm_to_m",
    "pixel_scale_meters",
    "pixel_to_projected",
    "projected_to_pixel",
    "rad_to_deg",
    "scale_dem_to_meters",
]
