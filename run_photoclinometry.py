"""Legacy runner preserved for compatibility.

Prefer `lunardem generate` CLI or the Python API in new workflows.
"""

from __future__ import annotations

from lunardem import ReconstructionConfig, generate_dem


def main() -> None:
    config = ReconstructionConfig(
        output={"output_dir": "output", "base_name": "reconstructed_dem"},
    )
    result = generate_dem("data/moon1.png", method="sfs", config=config)
    print("Generation complete.")
    print("Exports:", result.exports)
    if result.metrics:
        print("Elevation min/max (m):", result.metrics.stats["elevation_min_m"], result.metrics.stats["elevation_max_m"])


if __name__ == "__main__":
    main()
