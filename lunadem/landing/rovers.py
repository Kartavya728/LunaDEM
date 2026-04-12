"""Rover presets and typed rover specification helpers."""

from __future__ import annotations

from typing import Any, Mapping

from lunadem.core.models import RoverSpec

ROVER_LIBRARY: dict[str, RoverSpec] = {
    "sojourner": RoverSpec(
        name="sojourner",
        length_m=0.65,
        width_m=0.48,
        height_m=0.28,
        ground_clearance_m=0.17,
        safety_margin_m=0.15,
        source="NASA/JPL Sojourner rover dimensions",
    ),
    "spirit": RoverSpec(
        name="spirit",
        length_m=1.5,
        width_m=2.2,
        height_m=1.6,
        ground_clearance_m=0.25,
        safety_margin_m=0.4,
        source="NASA Mars Exploration Rovers dimensions",
    ),
    "opportunity": RoverSpec(
        name="opportunity",
        length_m=1.5,
        width_m=2.2,
        height_m=1.6,
        ground_clearance_m=0.25,
        safety_margin_m=0.4,
        source="NASA Mars Exploration Rovers dimensions",
    ),
    "curiosity": RoverSpec(
        name="curiosity",
        length_m=3.0,
        width_m=2.7,
        height_m=2.2,
        ground_clearance_m=0.45,
        safety_margin_m=0.6,
        source="NASA/JPL Curiosity rover dimensions",
    ),
    "perseverance": RoverSpec(
        name="perseverance",
        length_m=3.0,
        width_m=2.7,
        height_m=2.2,
        ground_clearance_m=0.45,
        safety_margin_m=0.6,
        source="NASA/JPL Perseverance rover dimensions",
    ),
    "pragyan": RoverSpec(
        name="pragyan",
        length_m=0.9,
        width_m=0.75,
        height_m=0.85,
        ground_clearance_m=0.18,
        safety_margin_m=0.2,
        source="ISRO Chandrayaan-2 rover dimensions",
    ),
    "soraq": RoverSpec(
        name="soraq",
        length_m=0.08,
        width_m=0.08,
        height_m=0.08,
        ground_clearance_m=0.03,
        safety_margin_m=0.05,
        source="JAXA LEV-2 / SORA-Q rover dimensions",
    ),
}


def get_rover_spec(
    name_or_custom_dims: str | RoverSpec | Mapping[str, Any] | None = None,
    *,
    length_m: float | None = None,
    width_m: float | None = None,
    height_m: float | None = None,
    ground_clearance_m: float | None = None,
    safety_margin_m: float | None = None,
) -> RoverSpec:
    """Return a rover spec from a known name or custom dimensions."""
    if isinstance(name_or_custom_dims, RoverSpec):
        return name_or_custom_dims

    if isinstance(name_or_custom_dims, Mapping):
        payload = dict(name_or_custom_dims)
        return RoverSpec(
            name=str(payload.get("name", "custom_rover")),
            length_m=float(payload["length_m"]),
            width_m=float(payload["width_m"]),
            height_m=float(payload["height_m"]),
            ground_clearance_m=float(payload.get("ground_clearance_m", 0.2)),
            safety_margin_m=float(payload.get("safety_margin_m", 0.25)),
            source=str(payload.get("source", "user-provided")),
            mesh_path=payload.get("mesh_path"),
            metadata=dict(payload.get("metadata", {})),
        )

    if isinstance(name_or_custom_dims, str):
        key = name_or_custom_dims.strip().lower()
        if key not in ROVER_LIBRARY:
            raise KeyError(f"Unknown rover preset {name_or_custom_dims!r}")
        return ROVER_LIBRARY[key]

    if length_m is None or width_m is None or height_m is None:
        raise ValueError("Provide a rover preset name/spec or explicit length_m, width_m, and height_m.")

    return RoverSpec(
        name="custom_rover",
        length_m=float(length_m),
        width_m=float(width_m),
        height_m=float(height_m),
        ground_clearance_m=float(ground_clearance_m if ground_clearance_m is not None else 0.2),
        safety_margin_m=float(safety_margin_m if safety_margin_m is not None else 0.25),
        source="user-provided",
    )
