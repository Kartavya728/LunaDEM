"""Multi-scale shape-from-shading method."""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
from scipy.ndimage import zoom

from lunadem.core.config import ReconstructionConfig
from lunadem.methods.base import MethodResult, ReconstructionMethod
from lunadem.methods.sfs import _prepare_working_surface, run_sfs_optimization


def _build_pyramid(image: np.ndarray, levels: int, factor: float) -> List[np.ndarray]:
    pyramid = [image]
    current = image
    for _ in range(levels - 1):
        current = zoom(current, zoom=factor, order=1)
        pyramid.append(current)
    pyramid.reverse()
    return pyramid


def _resize_dem(dem: np.ndarray, target_shape: Tuple[int, int]) -> np.ndarray:
    y_scale = target_shape[0] / dem.shape[0]
    x_scale = target_shape[1] / dem.shape[1]
    return zoom(dem, zoom=(y_scale, x_scale), order=1).astype(np.float32)


class MultiScaleSFSMethod(ReconstructionMethod):
    """Coarse-to-fine SFS method."""

    name = "multiscale_sfs"

    def run(
        self,
        image: np.ndarray,
        config: ReconstructionConfig,
        initial_dem: np.ndarray | None = None,
    ) -> MethodResult:
        original_shape = image.shape
        working_image, resample_scale = _prepare_working_surface(image, config)
        levels = config.sfs.multiscale_levels
        factor = config.sfs.downscale_factor
        pyramid = _build_pyramid(working_image, levels=levels, factor=factor)

        dem = initial_dem
        if dem is not None and dem.shape != working_image.shape:
            dem = _resize_dem(dem.astype(np.float32), working_image.shape)
        level_diagnostics: List[Dict[str, float | str | bool]] = []
        for level_index, level_image in enumerate(pyramid, start=1):
            if dem is not None:
                dem = _resize_dem(dem, level_image.shape)
            dem, diagnostics = run_sfs_optimization(
                image=level_image,
                config=config,
                initial_dem=dem,
            )
            diagnostics["level"] = float(level_index)
            diagnostics["height"] = float(level_image.shape[0])
            diagnostics["width"] = float(level_image.shape[1])
            level_diagnostics.append(diagnostics)

        if dem is not None and dem.shape != original_shape:
            dem = _resize_dem(dem, original_shape)

        return MethodResult(
            dem=dem.astype(np.float32),
            diagnostics={
                "levels": float(levels),
                "downscale_factor": float(factor),
                "original_height": float(original_shape[0]),
                "original_width": float(original_shape[1]),
                "working_height": float(working_image.shape[0]),
                "working_width": float(working_image.shape[1]),
                "resample_scale": float(resample_scale),
                "used_working_resolution": bool(resample_scale != 1.0),
                "per_level": level_diagnostics,
            },
        )
