"""Multi-scale shape-from-shading method."""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
from scipy.ndimage import zoom

from lunardem.core.config import ReconstructionConfig
from lunardem.methods.base import MethodResult, ReconstructionMethod
from lunardem.methods.sfs import run_sfs_optimization


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
        levels = config.sfs.multiscale_levels
        factor = config.sfs.downscale_factor
        pyramid = _build_pyramid(image, levels=levels, factor=factor)

        dem = initial_dem
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

        return MethodResult(
            dem=dem.astype(np.float32),
            diagnostics={
                "levels": float(levels),
                "downscale_factor": float(factor),
                "per_level": level_diagnostics,
            },
        )
