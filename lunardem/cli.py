"""Command-line interface for LunarDEM."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import typer

from lunardem import analyze_dem, assess_landing, generate_dem
from lunardem.core.config import AnalysisConfig, LandingConfig, ReconstructionConfig
from lunardem.utils.config import load_config_file

app = typer.Typer(help="LunarDEM CLI for DEM generation, analytics, and landing suitability.")


def _merge_overrides(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_overrides(merged[key], value)
        else:
            merged[key] = value
    return merged


@app.command("generate")
def generate_command(
    input_path: Path = typer.Argument(..., exists=True, help="Input image path."),
    method: str = typer.Option("sfs", "--method", "-m", help="Method: sfs, multiscale_sfs, ml, hybrid."),
    output: Path = typer.Option(Path("output"), "--output", "-o", help="Output directory."),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="JSON or YAML config file."),
) -> None:
    """Generate DEM from an image."""
    cfg_data: Dict[str, Any] = {}
    if config is not None:
        cfg_data = load_config_file(config)

    cfg_data = _merge_overrides(
        cfg_data,
        {
            "output": {
                "output_dir": str(output),
            }
        },
    )
    reconstruction_config = ReconstructionConfig.model_validate(cfg_data)
    result = generate_dem(input_data=input_path, method=method, config=reconstruction_config)

    payload = {
        "method": result.method,
        "pixel_scale_m": result.pixel_scale_m,
        "crs": result.crs,
        "exports": result.exports,
        "diagnostics": result.diagnostics,
        "stats": result.metrics.stats if result.metrics else {},
    }
    typer.echo(json.dumps(payload, indent=2))


@app.command("analyze")
def analyze_command(
    dem_path: Path = typer.Argument(..., exists=True, help="DEM path (.tif preferred)."),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="JSON or YAML analysis config."),
) -> None:
    """Analyze DEM terrain metrics."""
    cfg = AnalysisConfig()
    if config is not None:
        cfg = AnalysisConfig.model_validate(load_config_file(config))
    metrics = analyze_dem(dem_or_path=dem_path, analysis_config=cfg)
    payload = {
        "stats": metrics.stats,
    }
    typer.echo(json.dumps(payload, indent=2))


@app.command("landing")
def landing_command(
    dem_path: Path = typer.Argument(..., exists=True, help="DEM path."),
    spacecraft: Optional[Path] = typer.Option(
        None,
        "--spacecraft",
        "-s",
        help="Landing/spacecraft constraints config (JSON or YAML).",
    ),
) -> None:
    """Run landing suitability checks for a DEM."""
    cfg = LandingConfig()
    if spacecraft is not None:
        cfg = LandingConfig.model_validate(load_config_file(spacecraft))
    report = assess_landing(dem_or_path=dem_path, landing_config=cfg)
    payload = {
        "safe_fraction": report.safe_fraction,
        "score": report.score,
        "summary": report.summary,
    }
    typer.echo(json.dumps(payload, indent=2))


def main() -> None:
    """CLI entrypoint for console scripts."""
    app()


if __name__ == "__main__":
    main()
