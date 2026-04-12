"""Method registry for reconstruction backends."""

from __future__ import annotations

from typing import Dict, Iterable

from lunadem.methods.base import ReconstructionMethod


class MethodRegistry:
    """Runtime registry mapping method names to implementations."""

    def __init__(self) -> None:
        self._methods: Dict[str, ReconstructionMethod] = {}

    def register(self, method: ReconstructionMethod) -> None:
        self._methods[method.name] = method

    def get(self, name: str) -> ReconstructionMethod:
        if name not in self._methods:
            available = ", ".join(sorted(self._methods))
            raise KeyError(f"Unknown method '{name}'. Available methods: {available}")
        return self._methods[name]

    def names(self) -> Iterable[str]:
        return self._methods.keys()
