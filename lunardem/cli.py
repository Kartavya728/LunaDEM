"""Command-line interface for LunarDEM."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
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


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _resolve_asset(filename: str) -> Path:
    candidates = [
        Path.cwd() / filename,
        _project_root() / filename,
        _project_root() / "assets" / filename,
        _project_root() / "examples" / filename,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Required media file not found: {filename}")


def _open_with_default_app(path: Path) -> None:
    if sys.platform.startswith("win"):
        os.startfile(str(path))  # type: ignore[attr-defined]
        return
    if sys.platform == "darwin":
        subprocess.Popen(["open", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    subprocess.Popen(["xdg-open", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _play_fun_audio(repeat_count: int) -> None:
    if repeat_count <= 0:
        raise ValueError("Repeat count must be >= 1.")
    media = _resolve_asset("fun.mp3")
    for _ in range(repeat_count):
        _open_with_default_app(media)
        # Small spacing improves repeat behavior across default media apps.
        time.sleep(0.35)


def _show_babies_image() -> None:
    _open_with_default_app(_resolve_asset("japneet.jpeg"))


def _show_noor_video() -> None:
    _open_with_default_app(_resolve_asset("noor.mp4"))


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


def _print_lunadem_terminal_docs() -> None:
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table

        console = Console()
        console.print(
            Panel.fit(
                "[bold cyan]lunadem[/bold cyan]  [white]-[/white]  DEM Toolkit For Lunar And Planetary Imaging\n"
                "[dim]API import name: lunardem[/dim]\n"
                "[dim]PyPI: https://pypi.org/project/lunadem/0.1.1/[/dim]",
                title="Library Overview",
                border_style="blue",
            )
        )

        capability_table = Table(title="Core Capabilities", show_header=True, header_style="bold magenta")
        capability_table.add_column("Area", style="cyan", width=24)
        capability_table.add_column("Details", style="white")
        capability_table.add_row("DEM Methods", "sfs, multiscale_sfs, ml, hybrid")
        capability_table.add_row("Analytics", "slope, roughness, curvature, histograms")
        capability_table.add_row("Landing", "safe mask, hazard mask, score, safe fraction")
        capability_table.add_row("Exports", "GeoTIFF, OBJ/PLY, plots, JSON manifest")
        capability_table.add_row("Inputs", "PNG, JPG, TIFF, GeoTIFF, NumPy arrays")
        console.print(capability_table)

        command_table = Table(title="Primary CLI Commands", show_header=True, header_style="bold green")
        command_table.add_column("Command", style="green", width=22)
        command_table.add_column("Purpose", style="white")
        command_table.add_row("lunardem generate", "Generate DEM from image input")
        command_table.add_row("lunardem analyze", "Compute terrain statistics")
        command_table.add_row("lunardem landing", "Run deterministic landing suitability checks")
        console.print(command_table)
    except Exception:
        # Fallback for environments where rich cannot render.
        print("lunadem - DEM Toolkit")
        print("PyPI: https://pypi.org/project/lunadem/0.1.1/")
        print("Methods: sfs, multiscale_sfs, ml, hybrid")
        print("CLI: lunardem generate | lunardem analyze | lunardem landing")


def lunadem_main() -> None:
    """Entry command for `lunadem` that prints terminal documentation."""
    _print_lunadem_terminal_docs()


def kartavya_main() -> None:
    """Fun command: play `fun.mp3` with optional repeats."""
    parser = argparse.ArgumentParser(prog="kartavya", description="Play fun.mp3 on your device.")
    parser.add_argument("-n", type=int, default=1, help="Number of times to play audio.")
    args = parser.parse_args()
    if args.n <= 0:
        parser.error("-n must be >= 1")
    _play_fun_audio(args.n)


def babies_main() -> None:
    """Fun command: open japneet.jpeg."""
    _show_babies_image()


def noor_main() -> None:
    """Fun command: play noor.mp4."""
    _show_noor_video()


def overkill_main() -> None:
    """Fun command: run audio + image + video actions together."""
    parser = argparse.ArgumentParser(prog="overkill", description="Run all fun actions together.")
    parser.add_argument("-n", type=int, default=1, help="Number of times to play fun.mp3.")
    args = parser.parse_args()
    if args.n <= 0:
        parser.error("-n must be >= 1")

    workers = [
        threading.Thread(target=_play_fun_audio, args=(args.n,), daemon=True),
        threading.Thread(target=_show_babies_image, daemon=True),
        threading.Thread(target=_show_noor_video, daemon=True),
    ]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()


def main() -> None:
    """CLI entrypoint for console scripts."""
    app()


if __name__ == "__main__":
    main()
