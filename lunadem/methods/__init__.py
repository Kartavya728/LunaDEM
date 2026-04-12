"""Reconstruction methods."""

from lunadem.methods.hybrid import HybridMethod
from lunadem.methods.ml_models import MLMethod
from lunadem.methods.multiscale import MultiScaleSFSMethod
from lunadem.methods.sfs import SFSMethod


def register_default_methods(registry) -> None:
    """Register all built-in methods."""
    registry.register(SFSMethod())
    registry.register(MultiScaleSFSMethod())
    registry.register(MLMethod())
    registry.register(HybridMethod())
