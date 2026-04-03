"""Surface normal and reflectance computations."""

from __future__ import annotations

import numpy as np


def calculate_surface_normals(height_map: np.ndarray) -> np.ndarray:
    """Calculate normalized surface normals from DEM."""
    q, p = np.gradient(height_map)
    normals = np.stack([-p, -q, np.ones_like(height_map)], axis=-1)
    norms = np.linalg.norm(normals, axis=2, keepdims=True)
    safe_norms = np.maximum(norms, 1e-9)
    return normals / safe_norms


def calculate_predicted_image(height_map: np.ndarray, light_vec: np.ndarray) -> np.ndarray:
    """Compute Lambertian reflectance image from height map."""
    normals = calculate_surface_normals(height_map)
    reflectance = np.dot(normals, light_vec)
    return np.maximum(0.0, reflectance)
