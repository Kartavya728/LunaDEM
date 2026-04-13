"""Core API, configuration, and typed models with lazy exports."""

from __future__ import annotations

from importlib import import_module

_EXPORT_MAP = {
    "AnalysisConfig": ("lunadem.core.config", "AnalysisConfig"),
    "DEMResult": ("lunadem.core.models", "DEMResult"),
    "GeoreferenceConfig": ("lunadem.core.config", "GeoreferenceConfig"),
    "HybridMethodConfig": ("lunadem.core.config", "HybridMethodConfig"),
    "IlluminationConfig": ("lunadem.core.config", "IlluminationConfig"),
    "KaguyaScene": ("lunadem.core.models", "KaguyaScene"),
    "LandingConfig": ("lunadem.core.config", "LandingConfig"),
    "LandingConstraints": ("lunadem.core.config", "LandingConstraints"),
    "LandingReport": ("lunadem.core.models", "LandingReport"),
    "LandingSiteResult": ("lunadem.core.models", "LandingSiteResult"),
    "MLMethodConfig": ("lunadem.core.config", "MLMethodConfig"),
    "MetadataPrediction": ("lunadem.core.models", "MetadataPrediction"),
    "OutputConfig": ("lunadem.core.config", "OutputConfig"),
    "PreprocessingConfig": ("lunadem.core.config", "PreprocessingConfig"),
    "ReconstructionConfig": ("lunadem.core.config", "ReconstructionConfig"),
    "RoverSpec": ("lunadem.core.models", "RoverSpec"),
    "SFSMethodConfig": ("lunadem.core.config", "SFSMethodConfig"),
    "SceneGeometry": ("lunadem.core.models", "SceneGeometry"),
    "SensorConfig": ("lunadem.core.config", "SensorConfig"),
    "TerrainMetrics": ("lunadem.core.models", "TerrainMetrics"),
    "analyze_dem": ("lunadem.core.api", "analyze_dem"),
    "assess_landing": ("lunadem.core.api", "assess_landing"),
    "generate_dem": ("lunadem.core.api", "generate_dem"),
}

__all__ = list(_EXPORT_MAP)


def __getattr__(name: str):
    if name not in _EXPORT_MAP:
        raise AttributeError(f"module 'lunadem.core' has no attribute {name!r}")
    module_name, attribute_name = _EXPORT_MAP[name]
    module = import_module(module_name)
    value = getattr(module, attribute_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(__all__)
