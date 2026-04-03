from __future__ import annotations

from lunardem.core.config import ReconstructionConfig
from lunardem.methods.multiscale import MultiScaleSFSMethod


def test_multiscale_method_runs(synthetic_image) -> None:
    method = MultiScaleSFSMethod()
    config = ReconstructionConfig(
        sfs={
            "max_iterations": 6,
            "multiscale_levels": 2,
            "downscale_factor": 0.5,
        },
        preprocessing={"shadow_mask": False},
    )
    result = method.run(synthetic_image, config=config)
    assert result.dem.shape == synthetic_image.shape
    assert "per_level" in result.diagnostics
