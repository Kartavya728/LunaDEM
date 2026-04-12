"""Array preprocessing helpers."""

from __future__ import annotations

import numpy as np


def normalize_to_unit_range(array: np.ndarray) -> np.ndarray:
    """Normalize an array to [0, 1].

    Parameters
    ----------
    array:
        Input array.

    Returns
    -------
    np.ndarray
        Float32 normalized array. Returns zeros when range is degenerate.
    """
    arr = np.asarray(array, dtype=np.float32)
    min_val = float(np.min(arr))
    max_val = float(np.max(arr))
    if max_val <= min_val:
        return np.zeros_like(arr, dtype=np.float32)
    return ((arr - min_val) / (max_val - min_val)).astype(np.float32)
