from __future__ import annotations

from pathlib import Path

import numpy as np

from lunardem import (
    AnalysisConfig,
    LandingConfig,
    ReconstructionConfig,
    analyze_dem,
    assess_landing,
    generate_dem,
)


def test_end_to_end_generate_analyze_landing(synthetic_image_path: Path, tmp_path: Path) -> None:
    config = ReconstructionConfig(
        output={
            "output_dir": str(tmp_path),
            "base_name": "integration",
            "save_visualizations": False,
        },
        sfs={"max_iterations": 8},
        preprocessing={"shadow_mask": False},
    )
    dem_result = generate_dem(synthetic_image_path, method="sfs", config=config)
    assert dem_result.dem_meters.shape == (32, 32)
    assert dem_result.exports["geotiff"] is not None

    metrics = analyze_dem(
        dem_result.dem_meters,
        analysis_config=AnalysisConfig(pixel_size_m=dem_result.pixel_scale_m),
    )
    assert "slope_mean_deg" in metrics.stats

    report = assess_landing(
        dem_result.dem_meters,
        landing_config=LandingConfig(pixel_size_m=dem_result.pixel_scale_m),
    )
    assert isinstance(report.safe_fraction, float)
    assert report.safe_mask.dtype == np.uint8
