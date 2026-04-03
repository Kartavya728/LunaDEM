from __future__ import annotations

from lunardem.core.config import ReconstructionConfig
from lunardem.methods.sfs import SFSMethod


def test_sfs_method_runs_on_synthetic_image(synthetic_image) -> None:
    method = SFSMethod()
    config = ReconstructionConfig(
        sfs={
            "max_iterations": 10,
            "regularization_lambda": 0.01,
        },
        preprocessing={"shadow_mask": False},
    )
    result = method.run(synthetic_image, config=config)
    assert result.dem.shape == synthetic_image.shape
    assert "success" in result.diagnostics
