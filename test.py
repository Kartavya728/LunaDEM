from lunardem import generate_dem, ReconstructionConfig

config = ReconstructionConfig(
    output={"output_dir": "output", "base_name": "moon_run"},
)
result = generate_dem("data/moon1.png", method="multiscale_sfs", config=config)
print(result.exports)
print(result.metrics.stats)