from __future__ import annotations

import numpy as np

from lunadem.geometry.lighting import get_light_vector


def test_light_vector_is_unit_length() -> None:
    vec = get_light_vector(120.0, 35.0)
    assert np.isclose(np.linalg.norm(vec), 1.0, atol=1e-6)


def test_light_vector_points_upward_for_positive_elevation() -> None:
    vec = get_light_vector(45.0, 10.0)
    assert vec[2] > 0.0
