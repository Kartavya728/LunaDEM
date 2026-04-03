"""Geometry and planetary coordinate utilities."""

from lunardem.geometry.lighting import get_light_vector
from lunardem.geometry.planetary import DEFAULT_MOON_CRS, MOON_RADIUS_M
from lunardem.geometry.scaling import pixel_scale_meters, scale_dem_to_meters
from lunardem.geometry.surface import calculate_predicted_image, calculate_surface_normals

__all__ = [
    "DEFAULT_MOON_CRS",
    "MOON_RADIUS_M",
    "calculate_predicted_image",
    "calculate_surface_normals",
    "get_light_vector",
    "pixel_scale_meters",
    "scale_dem_to_meters",
]
