"""ML-based reconstruction scaffolding."""

from __future__ import annotations

from typing import Dict

import numpy as np
from scipy.ndimage import gaussian_filter

from lunardem.core.config import ReconstructionConfig
from lunardem.methods.base import MethodResult, ReconstructionMethod
from lunardem.utils.arrays import normalize_to_unit_range


def _torch_available() -> bool:
    try:
        import torch  # noqa: F401

        return True
    except Exception:
        return False


class MLMethod(ReconstructionMethod):
    """Plugin-ready ML DEM method with deterministic baseline fallback."""

    name = "ml"

    def run(
        self,
        image: np.ndarray,
        config: ReconstructionConfig,
        initial_dem: np.ndarray | None = None,
    ) -> MethodResult:
        normalized = normalize_to_unit_range(image)
        baseline = 1.0 - normalized
        baseline = gaussian_filter(
            baseline,
            sigma=config.ml.fallback_smoothing_sigma,
        ).astype(np.float32)
        baseline -= float(np.mean(baseline))

        diagnostics: Dict[str, float | str | bool] = {
            "torch_available": _torch_available(),
            "used_pretrained_model": False,
            "model_path": config.ml.model_path or "",
            "mode": "deterministic_baseline",
        }
        return MethodResult(dem=baseline, diagnostics=diagnostics)
