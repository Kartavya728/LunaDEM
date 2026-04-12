"""Optional native acceleration hooks with Python fallbacks."""

from __future__ import annotations

from typing import Callable

import numpy as np

NativeLightVectorFn = Callable[[float, float], np.ndarray]
NativeHazardMapFn = Callable[[np.ndarray, int], np.ndarray]

try:
    from lunadem import _native as _native_impl  # type: ignore[attr-defined]

    native_compute_light_vector: NativeLightVectorFn | None = _native_impl.compute_light_vector
    native_hazard_map: NativeHazardMapFn | None = _native_impl.hazard_map
except Exception:
    native_compute_light_vector = None
    native_hazard_map = None
