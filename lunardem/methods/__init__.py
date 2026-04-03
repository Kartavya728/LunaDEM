"""Reconstruction methods."""

from lunardem.methods.hybrid import HybridMethod
from lunardem.methods.ml_models import MLMethod
from lunardem.methods.multiscale import MultiScaleSFSMethod
from lunardem.methods.sfs import SFSMethod


def register_default_methods(registry) -> None:
    """Register all built-in methods."""
    registry.register(SFSMethod())
    registry.register(MultiScaleSFSMethod())
    registry.register(MLMethod())
    registry.register(HybridMethod())
