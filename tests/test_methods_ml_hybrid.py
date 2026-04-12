from __future__ import annotations

from lunadem.core.config import ReconstructionConfig
from lunadem.methods.hybrid import HybridMethod
from lunadem.methods.ml_models import MLMethod


def test_ml_method_baseline_runs(synthetic_image) -> None:
    method = MLMethod()
    config = ReconstructionConfig()
    result = method.run(synthetic_image, config=config)
    assert result.dem.shape == synthetic_image.shape
    assert result.diagnostics["mode"] == "deterministic_baseline"


def test_hybrid_method_runs(synthetic_image) -> None:
    method = HybridMethod()
    config = ReconstructionConfig(
        sfs={"max_iterations": 5},
        preprocessing={"shadow_mask": False},
    )
    result = method.run(synthetic_image, config=config)
    assert result.dem.shape == synthetic_image.shape
    assert "blend_weight" in result.diagnostics
