"""Landing analysis and rover helpers with lazy exports."""

from __future__ import annotations

from importlib import import_module

_EXPORT_MAP = {
    "assess_landing_suitability": ("lunadem.landing.suitability", "assess_landing_suitability"),
    "compute_terrain_metrics": ("lunadem.landing.analysis", "compute_terrain_metrics"),
    "find_safe_landing_site": ("lunadem.landing.sites", "find_safe_landing_site"),
    "get_rover_spec": ("lunadem.landing.rovers", "get_rover_spec"),
    "list_available_rovers": ("lunadem.landing.rovers", "list_available_rovers"),
}

__all__ = list(_EXPORT_MAP)


def __getattr__(name: str):
    if name not in _EXPORT_MAP:
        raise AttributeError(f"module 'lunadem.landing' has no attribute {name!r}")
    module_name, attribute_name = _EXPORT_MAP[name]
    module = import_module(module_name)
    value = getattr(module, attribute_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(__all__)
