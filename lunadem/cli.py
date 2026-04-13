"""Command-line interface for lunadem."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
import sys
import threading
import time
from typing import Any, Dict, Optional

import typer

try:
    import numpy as np
except Exception:  # pragma: no cover - only used in broken runtime environments
    np = None  # type: ignore[assignment]

import lunadem as api
from lunadem import TEST_SCENE_ID, __version__, download_test_scene
from lunadem.branding import CREATOR_GITHUB_ID, CREATOR_NAME, add_matplotlib_credit
from lunadem.core.config import AnalysisConfig, LandingConfig, ReconstructionConfig
from lunadem.utils.config import load_config_file

app = typer.Typer(help="lunadem CLI for DEM generation, metadata analysis, landing safety, and visualization.")
PYPI_PROJECT_URL = "https://pypi.org/project/lunadem/"


def _json_ready(value: Any) -> Any:
    if is_dataclass(value):
        return _json_ready(asdict(value))
    if isinstance(value, Path):
        return str(value)
    if np is not None and isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {str(key): _json_ready(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def _echo_json(payload: Any) -> None:
    typer.echo(json.dumps(_json_ready(payload), indent=2))


def _merge_overrides(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_overrides(merged[key], value)
        else:
            merged[key] = value
    return merged


def _resolve_asset(filename: str) -> Path:
    asset = Path(__file__).resolve().parent / "assets" / filename
    if asset.exists():
        return asset
    raise FileNotFoundError(
        f"Required packaged media file missing: {filename}. "
        "Reinstall package to ensure assets are bundled."
    )


def _play_fun_audio(repeat_count: int) -> None:
    try:
        import pygame
    except ImportError as exc:
        raise RuntimeError("pygame is required for internal audio playback.") from exc

    if repeat_count <= 0:
        raise ValueError("Repeat count must be >= 1.")
    media = _resolve_asset("fun.mp3")

    pygame.mixer.init()
    try:
        for _ in range(repeat_count):
            pygame.mixer.music.load(str(media))
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
    finally:
        pygame.mixer.music.stop()
        pygame.mixer.quit()


def _show_babies_image(block: bool = True) -> None:
    import imageio.v2 as imageio
    import matplotlib.pyplot as plt

    image = imageio.imread(_resolve_asset("japneet.jpeg"))
    fig, ax = plt.subplots(num="babies")
    ax.imshow(image)
    ax.set_title("babies")
    ax.axis("off")
    add_matplotlib_credit(fig)
    plt.tight_layout()
    if block:
        plt.show()
    else:
        plt.show(block=False)
        plt.pause(0.1)


def _show_noor_video(block: bool = True) -> None:
    import imageio.v2 as imageio
    import matplotlib.pyplot as plt

    video_path = _resolve_asset("noor.mp4")
    reader = imageio.get_reader(video_path)
    metadata = reader.get_meta_data()
    fps = float(metadata.get("fps", 24.0))
    frame_delay = 1.0 / max(fps, 1.0)

    fig, ax = plt.subplots(num="noor")
    ax.axis("off")
    frame_iter = iter(reader)
    first_frame = next(frame_iter)
    image_plot = ax.imshow(first_frame)
    ax.set_title("noor")
    add_matplotlib_credit(fig)
    plt.tight_layout()
    plt.show(block=False)
    plt.pause(0.1)

    for frame in frame_iter:
        image_plot.set_data(frame)
        plt.pause(frame_delay)

    reader.close()
    if block:
        plt.show()


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

    cfg_data = _merge_overrides(cfg_data, {"output": {"output_dir": str(output)}})
    reconstruction_config = ReconstructionConfig.model_validate(cfg_data)
    result = api.generate_dem(input_data=input_path, method=method, config=reconstruction_config)

    payload = {
        "method": result.method,
        "pixel_scale_m": result.pixel_scale_m,
        "crs": result.crs,
        "exports": result.exports,
        "diagnostics": result.diagnostics,
        "stats": result.metrics.stats if result.metrics else {},
    }
    _echo_json(payload)


@app.command("analyze")
def analyze_command(
    dem_path: Path = typer.Argument(..., exists=True, help="DEM path (.tif preferred)."),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="JSON or YAML analysis config."),
) -> None:
    """Analyze DEM terrain metrics."""
    cfg = AnalysisConfig()
    if config is not None:
        cfg = AnalysisConfig.model_validate(load_config_file(config))
    metrics = api.analyze_dem(dem_or_path=dem_path, analysis_config=cfg)
    _echo_json({"stats": metrics.stats})


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
    report = api.assess_landing(dem_or_path=dem_path, landing_config=cfg)
    payload = {
        "safe_fraction": report.safe_fraction,
        "score": report.score,
        "summary": report.summary,
    }
    _echo_json(payload)


@app.command("sfs")
def sfs_command(
    maths: bool = typer.Option(False, "--maths", help="Show the SFS mathematics reference."),
    terms: bool = typer.Option(False, "--terms", help="Show the SFS terminology reference."),
    assumptions: bool = typer.Option(False, "--assumptions", help="Show SFS assumptions and caveats."),
) -> None:
    """Explain the shape-from-shading method used by lunadem."""
    selected = int(maths) + int(terms) + int(assumptions)
    if selected != 1:
        raise typer.BadParameter("Choose exactly one of --maths, --terms, or --assumptions.")
    if maths:
        typer.echo(api.get_sfs_math())
    elif terms:
        typer.echo(api.get_sfs_terms())
    else:
        typer.echo(api.get_sfs_assumptions())


@app.command("download")
def download_command(
    test: bool = typer.Option(False, "--test", help="Download the official packaged test scene."),
    output: Path = typer.Option(Path("downloads"), "--output", "-o", help="Target output directory."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing files."),
) -> None:
    """Download packaged reference data."""
    if not test:
        raise typer.BadParameter("Only --test is currently supported.")
    payload = {
        "scene_id": TEST_SCENE_ID,
        "downloads": download_test_scene(output_dir=output, overwrite=overwrite),
    }
    _echo_json(payload)


@app.command("scene-summary")
def scene_summary_command(
    scene: str = typer.Argument(TEST_SCENE_ID, help="Scene ID, scene folder, or item.json path."),
    camera: Optional[Path] = typer.Option(None, "--camera", "-c", help="Optional camera.json path."),
) -> None:
    """Summarize a local Kaguya scene and derive metadata values."""
    camera_model = api.load_camera_model(camera) if camera is not None else api.load_camera_model(scene)
    _echo_json(api.build_scene_summary(scene, camera_model=camera_model))


@app.command("predict")
def predict_command(
    input_path: Path = typer.Argument(..., exists=True, help="Input image or TIFF path."),
    kind: str = typer.Option("all", "--kind", "-k", help="illumination, view, location, or all."),
    max_patches: int = typer.Option(16, "--max-patches", help="Maximum patches to aggregate per prediction."),
) -> None:
    """Run packaged metadata CNN predictors."""
    kind_normalized = kind.strip().lower()
    if kind_normalized == "illumination":
        prediction = api.predict_illumination(input_path, max_patches=max_patches)
    elif kind_normalized == "view":
        prediction = api.predict_view_geometry(input_path, max_patches=max_patches)
    elif kind_normalized == "location":
        prediction = api.predict_scene_location(input_path, max_patches=max_patches)
    elif kind_normalized == "all":
        prediction = api.predict_scene_metadata(input_path, max_patches=max_patches)
    else:
        raise typer.BadParameter("kind must be one of: illumination, view, location, all")

    payload = {"prediction": prediction, "available_metrics": api.get_model_metrics()}
    _echo_json(payload)


@app.command("landing-site")
def landing_site_command(
    input_path: Path = typer.Argument(..., exists=True, help="Input image, TIFF, or DEM path."),
    rover: str = typer.Option("pragyan", "--rover", "-r", help="Built-in rover preset name."),
    scene: Optional[str] = typer.Option(None, "--scene", "-s", help="Optional local scene ID or scene folder."),
    method: str = typer.Option("hybrid", "--method", "-m", help="Reconstruction method for image inputs."),
    backend: str = typer.Option("both", "--backend", "-b", help="matplotlib, plotly, or both."),
    show: bool = typer.Option(True, "--show/--no-show", help="Display the plots while also supporting save output."),
    output_2d_png: Optional[Path] = typer.Option(None, "--output-2d", help="Optional 2D Matplotlib plot output."),
    output_3d_png: Optional[Path] = typer.Option(None, "--output-3d", help="Optional 3D Matplotlib plot output."),
    output_2d_html: Optional[Path] = typer.Option(None, "--output-2d-html", help="Optional 2D landing plot HTML output."),
    output_3d_html: Optional[Path] = typer.Option(None, "--output-3d-html", help="Optional 3D landing plot HTML output."),
) -> None:
    """Find the safest rover landing site from an image or DEM."""
    scene_obj = api.load_kaguya_scene(scene) if scene else None
    result = api.find_safe_landing_site(input_path, rover=rover, scene=scene_obj, method=method)

    api.plot_landing_site_2d(
        input_path,
        result,
        backend=backend,
        show=show,
        save_path=output_2d_png,
        html_path=output_2d_html,
    )
    api.plot_landing_site_3d(
        input_path,
        result,
        backend=backend,
        show=show,
        save_path=output_3d_png,
        html_path=output_3d_html,
    )

    outputs: Dict[str, Optional[str]] = {
        "plot_2d_png": str(output_2d_png) if output_2d_png is not None else None,
        "plot_3d_png": str(output_3d_png) if output_3d_png is not None else None,
        "plot_2d_html": str(output_2d_html) if output_2d_html is not None else None,
        "plot_3d_html": str(output_3d_html) if output_3d_html is not None else None,
    }

    payload = {"landing_site": result, "outputs": outputs}
    _echo_json(payload)


@app.command("plot-scene")
def plot_scene_command(
    scene: str = typer.Argument(TEST_SCENE_ID, help="Scene ID or scene directory."),
    backend: str = typer.Option("both", "--backend", "-b", help="matplotlib, plotly, or both."),
    show: bool = typer.Option(True, "--show/--no-show", help="Display the scene plot."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Optional Matplotlib figure output path."),
    output_html: Optional[Path] = typer.Option(Path("scene_geometry.html"), "--output-html", help="Optional Plotly HTML output path."),
) -> None:
    """Render Moon, footprint, camera, sun, and Earth in 3D."""
    scene_obj = api.load_kaguya_scene(scene)
    api.plot_scene_geometry_3d(
        scene_obj,
        backend=backend,
        show=show,
        save_path=output,
        html_path=output_html,
    )
    api.plot_moon_surface_3d(
        scene_obj,
        backend=backend,
        show=False,
        save_path=output.with_name(f"{output.stem}_moon{output.suffix}") if output is not None else None,
        html_path=output_html.with_name(f"{output_html.stem}_moon{output_html.suffix}") if output_html is not None else None,
    )
    _echo_json(
        {
            "scene_id": scene_obj.scene_id,
            "backend": backend,
            "output": str(output) if output is not None else None,
            "output_html": str(output_html) if output_html is not None else None,
        }
    )


@app.command("plot-surface")
def plot_surface_command(
    input_path: Path = typer.Argument(..., exists=True, help="Image, TIFF, or DEM path."),
    backend: str = typer.Option("both", "--backend", "-b", help="matplotlib, plotly, or both."),
    show: bool = typer.Option(True, "--show/--no-show", help="Display the surface plot."),
    reconstruct: bool = typer.Option(False, "--reconstruct", help="Run DEM reconstruction before plotting."),
    method: str = typer.Option("hybrid", "--method", "-m", help="Reconstruction method when --reconstruct is used."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Optional Matplotlib figure output path."),
    output_html: Optional[Path] = typer.Option(Path("surface_plot.html"), "--output-html", help="Optional Plotly HTML output path."),
) -> None:
    """Plot a terrain surface from an image or DEM using Matplotlib, Plotly, or both."""
    surface_input: Any = input_path
    if reconstruct:
        reconstruction = ReconstructionConfig(
            output={
                "output_dir": "output",
                "base_name": "plot_surface",
                "save_geotiff": False,
                "save_obj": False,
                "save_ply": False,
                "save_visualizations": False,
                "save_interactive_html": False,
                "save_manifest": False,
            }
        )
        surface_input = api.generate_dem(input_path, method=method, config=reconstruction).dem_meters

    if backend in {"matplotlib", "both"}:
        api.plot_3d_surface(surface_input, save_path=output, show=show)
    if backend in {"plotly", "both"}:
        api.plot_3d_surface_interactive(
            surface_input,
            save_path=output_html if backend == "plotly" else (output_html or Path("surface_plot.html")),
            show=show and backend == "plotly",
        )

    _echo_json(
        {
            "backend": backend,
            "reconstructed": reconstruct,
            "output": str(output) if output is not None else None,
            "output_html": str(output_html) if output_html is not None else None,
        }
    )


def _print_lunadem_terminal_docs() -> None:
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table

        console = Console()
        console.print(
            Panel.fit(
                "[bold cyan]lunadem[/bold cyan]  [white]-[/white]  DEM Toolkit For Lunar And Planetary Imaging\n"
                "[dim]API import name: lunadem[/dim]\n"
                f"[dim]Installed version: {__version__}[/dim]\n"
                f"[dim]PyPI: {PYPI_PROJECT_URL}[/dim]",
                title="Library Overview",
                border_style="blue",
            )
        )

        capability_table = Table(title="Core Capabilities", show_header=True, header_style="bold magenta")
        capability_table.add_column("Area", style="cyan", width=24)
        capability_table.add_column("Details", style="white")
        capability_table.add_row("DEM Methods", "sfs, multiscale_sfs, ml, hybrid")
        capability_table.add_row("Metadata", "scene summary, STAC/camera derivations, packaged ONNX predictors")
        capability_table.add_row("Landing", "safe mask, rover-aware site selection, plotting in 2D and 3D")
        capability_table.add_row("Visualization", "Matplotlib + Plotly surface, Moon, landing, and space geometry")
        capability_table.add_row("Data", "download --test, local Kaguya scene loaders, 40+ callable APIs")
        console.print(capability_table)

        command_table = Table(title="Primary CLI Commands", show_header=True, header_style="bold green")
        command_table.add_column("Command", style="green", width=22)
        command_table.add_column("Purpose", style="white")
        command_table.add_row("lunadem generate", "Generate DEM from image input")
        command_table.add_row("lunadem scene-summary", "Explain and derive scene metadata")
        command_table.add_row("lunadem sfs --maths", "Show shape-from-shading theory")
        command_table.add_row("lunadem predict", "Run bundled metadata CNNs")
        command_table.add_row("lunadem landing-site", "Select the safest rover landing spot")
        command_table.add_row("lunadem plot-surface", "Show a DEM or image as a 3D surface")
        command_table.add_row("lunadem plot-scene", "Show Moon, footprint, camera, sun, and Earth")
        command_table.add_row("lunadem download --test", "Download the official test scene")
        console.print(command_table)
        console.print("[dim]Compatibility alias also available:[/dim] [bold]lunardem[/bold]")
    except Exception:
        print("lunadem - DEM Toolkit")
        print(f"Installed version: {__version__}")
        print(f"PyPI: {PYPI_PROJECT_URL}")
        print("Commands: generate | scene-summary | sfs | predict | landing-site | plot-surface | plot-scene | download --test")
        print("Compatibility alias: lunardem")


def lunadem_main() -> None:
    """Entry command for `lunadem` that shows docs or dispatches CLI commands."""
    parser = argparse.ArgumentParser(prog="lunadem", add_help=False)
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--docs", action="store_true")
    known, remaining = parser.parse_known_args()
    if known.version:
        print(__version__)
        return
    if known.docs or (len(sys.argv) == 1 and not remaining):
        _print_lunadem_terminal_docs()
        return
    app(prog_name="lunadem")


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
    _show_babies_image(block=True)


def noor_main() -> None:
    """Fun command: play noor.mp4."""
    _show_noor_video(block=True)


def overkill_main() -> None:
    """Fun command: run audio + image + video actions together."""
    parser = argparse.ArgumentParser(prog="overkill", description="Run all fun actions together.")
    parser.add_argument("-n", type=int, default=1, help="Number of times to play fun.mp3.")
    args = parser.parse_args()
    if args.n <= 0:
        parser.error("-n must be >= 1")

    audio_worker = threading.Thread(target=_play_fun_audio, args=(args.n,), daemon=True)
    audio_worker.start()
    _show_babies_image(block=False)
    _show_noor_video(block=True)
    audio_worker.join()


def creator_main() -> None:
    """Print creator identity details."""
    parser = argparse.ArgumentParser(prog="creator", description="Show creator details.")
    parser.add_argument("--info", action="store_true", help="Print full creator details.")
    args = parser.parse_args()
    if args.info:
        print(CREATOR_NAME)
        print(CREATOR_GITHUB_ID)
        return
    print(CREATOR_GITHUB_ID)


def main() -> None:
    """CLI entrypoint for console scripts."""
    lunadem_main()


if __name__ == "__main__":
    main()
