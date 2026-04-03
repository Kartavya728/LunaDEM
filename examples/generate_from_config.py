"""Generate DEM with external YAML/JSON config."""

from lunardem import ReconstructionConfig, generate_dem
from lunardem.utils.config import load_config_file


def main() -> None:
    cfg_dict = load_config_file("examples/configs/reconstruction.yaml")
    config = ReconstructionConfig.model_validate(cfg_dict)
    result = generate_dem("data/moon1.png", method="multiscale_sfs", config=config)
    print(result.exports)


if __name__ == "__main__":
    main()
