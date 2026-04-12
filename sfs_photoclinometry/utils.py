"""Legacy compatibility wrappers for geometry utilities."""

from __future__ import annotations

import numpy as np

from lunadem.geometry.lighting import get_light_vector
from lunadem.geometry.surface import calculate_predicted_image, calculate_surface_normals

__all__ = [
    "calculate_predicted_image",
    "calculate_surface_normals",
    "get_light_vector",
]

