"""Method base interfaces."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

import numpy as np

from lunardem.core.config import ReconstructionConfig


@dataclass
class MethodResult:
    """Internal method execution result."""

    dem: np.ndarray
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ReconstructionMethod:
    """Base reconstruction method contract."""

    name: str = "base"

    def run(
        self,
        image: np.ndarray,
        config: ReconstructionConfig,
        initial_dem: np.ndarray | None = None,
    ) -> MethodResult:
        raise NotImplementedError
