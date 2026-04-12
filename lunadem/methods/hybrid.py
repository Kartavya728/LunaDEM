"""Hybrid SFS + ML reconstruction."""

from __future__ import annotations

import numpy as np

from lunadem.core.config import ReconstructionConfig
from lunadem.methods.base import MethodResult, ReconstructionMethod
from lunadem.methods.ml_models import MLMethod
from lunadem.methods.sfs import SFSMethod


class HybridMethod(ReconstructionMethod):
    """Blend SFS output with ML prior."""

    name = "hybrid"

    def __init__(self) -> None:
        self._sfs = SFSMethod()
        self._ml = MLMethod()

    def run(
        self,
        image: np.ndarray,
        config: ReconstructionConfig,
        initial_dem: np.ndarray | None = None,
    ) -> MethodResult:
        sfs_result = self._sfs.run(image=image, config=config, initial_dem=initial_dem)

        try:
            ml_result = self._ml.run(image=image, config=config, initial_dem=initial_dem)
            ml_failed = False
        except Exception as exc:
            if not config.hybrid.fallback_to_sfs_on_ml_failure:
                raise
            ml_result = MethodResult(
                dem=np.zeros_like(sfs_result.dem),
                diagnostics={"error": str(exc), "fallback_used": True},
            )
            ml_failed = True

        w = float(config.hybrid.blend_weight)
        dem = (w * sfs_result.dem) + ((1.0 - w) * ml_result.dem)
        dem = dem.astype(np.float32)

        diagnostics = {
            "blend_weight": w,
            "ml_failed": ml_failed,
            "sfs": sfs_result.diagnostics,
            "ml": ml_result.diagnostics,
        }
        return MethodResult(dem=dem, diagnostics=diagnostics)
