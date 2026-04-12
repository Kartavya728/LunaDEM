from __future__ import annotations

import pytest
from pydantic import ValidationError

from lunadem.core.config import AnalysisConfig, IlluminationConfig


def test_invalid_illumination_raises() -> None:
    with pytest.raises(ValidationError):
        IlluminationConfig(sun_azimuth_deg=400.0, sun_elevation_deg=30.0)


def test_analysis_window_must_be_odd() -> None:
    with pytest.raises(ValidationError):
        AnalysisConfig(roughness_window=4)
