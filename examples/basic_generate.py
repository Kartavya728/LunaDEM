"""Basic lunadem API example."""

from lunadem import ReconstructionConfig, generate_dem


def main() -> None:
    config = ReconstructionConfig(
        output={"output_dir": "output", "base_name": "example_run"},
    )
    result = generate_dem("data/moon1.png", method="sfs", config=config)
    print("Exports:", result.exports)
    if result.metrics:
        print("Stats:", result.metrics.stats)


if __name__ == "__main__":
    main()
