"""Backward compatibility package for lunardem."""

from __future__ import annotations

import warnings

warnings.warn(
    "'lunardem' is deprecated; use 'lunadem' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from lunadem import *  # noqa: F401,F403
from lunadem import __all__, __version__  # noqa: F401