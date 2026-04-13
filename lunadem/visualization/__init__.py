"""Visualization helpers with Matplotlib and Plotly backends."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from lunadem.visualization.interactive import (
    plot_3d_surface_interactive,
    plot_landing_site_2d as _plot_landing_site_2d_plotly,
    plot_landing_site_3d as _plot_landing_site_3d_plotly,
    plot_moon_surface_3d as _plot_moon_surface_3d_plotly,
    plot_scene_geometry_3d as _plot_scene_geometry_3d_plotly,
)
from lunadem.visualization.plots import (
    plot_3d_surface,
    plot_depth_map,
    plot_landing_site_2d_matplotlib,
    plot_landing_site_3d_matplotlib,
    plot_moon_surface_3d as _plot_moon_surface_3d_matplotlib,
    plot_scene_geometry_3d_matplotlib,
    show_depth_map,
    show_surface_3d,
)

PlotBackend = str


def _default_html_path(save_path: str | Path | None, suffix: str) -> str | Path | None:
    if save_path is None:
        return None
    path = Path(save_path)
    if path.suffix.lower() == ".html":
        return path
    return path.with_name(f"{path.stem}{suffix}.html")


def _backend_payload(plotly_figure: Any | None, matplotlib_figure: Any | None, backend: PlotBackend) -> Any:
    if backend == "plotly":
        return plotly_figure
    if backend == "matplotlib":
        return matplotlib_figure
    return {"plotly": plotly_figure, "matplotlib": matplotlib_figure}


def plot_landing_site_2d(
    image_or_surface,
    landing_result,
    *,
    backend: PlotBackend = "plotly",
    show: bool = False,
    save_path: str | Path | None = None,
    html_path: str | Path | None = None,
    block: bool = True,
    title: str = "Safe Landing Site",
):
    """Plot a 2D landing-site overlay with Plotly, Matplotlib, or both."""
    if backend not in {"plotly", "matplotlib", "both"}:
        raise ValueError("backend must be 'plotly', 'matplotlib', or 'both'")

    plotly_figure = None
    matplotlib_figure = None
    if backend in {"plotly", "both"}:
        plotly_target = html_path if html_path is not None else (save_path if backend == "plotly" else _default_html_path(save_path, "_interactive"))
        plotly_figure = _plot_landing_site_2d_plotly(
            image_or_surface,
            landing_result,
            title=title,
            save_path=plotly_target,
            show=show and backend == "plotly",
        )
    if backend in {"matplotlib", "both"}:
        matplotlib_figure = plot_landing_site_2d_matplotlib(
            image_or_surface,
            landing_result,
            save_path=save_path if backend != "plotly" else None,
            title=title,
            show=show,
            block=block,
        )
    return _backend_payload(plotly_figure, matplotlib_figure, backend)


def plot_landing_site_3d(
    surface_or_dem,
    landing_result,
    *,
    backend: PlotBackend = "plotly",
    show: bool = False,
    save_path: str | Path | None = None,
    html_path: str | Path | None = None,
    block: bool = True,
    title: str = "3D Landing Site Visualization",
):
    """Plot a 3D landing-site visualization with Plotly, Matplotlib, or both."""
    if backend not in {"plotly", "matplotlib", "both"}:
        raise ValueError("backend must be 'plotly', 'matplotlib', or 'both'")

    plotly_figure = None
    matplotlib_figure = None
    if backend in {"plotly", "both"}:
        plotly_target = html_path if html_path is not None else (save_path if backend == "plotly" else _default_html_path(save_path, "_interactive"))
        plotly_figure = _plot_landing_site_3d_plotly(
            surface_or_dem,
            landing_result,
            title=title,
            save_path=plotly_target,
            show=show and backend == "plotly",
        )
    if backend in {"matplotlib", "both"}:
        matplotlib_figure = plot_landing_site_3d_matplotlib(
            surface_or_dem,
            landing_result,
            save_path=save_path if backend != "plotly" else None,
            title=title,
            show=show,
            block=block,
        )
    return _backend_payload(plotly_figure, matplotlib_figure, backend)


def plot_scene_geometry_3d(
    scene,
    *,
    backend: PlotBackend = "plotly",
    show: bool = False,
    save_path: str | Path | None = None,
    html_path: str | Path | None = None,
    block: bool = True,
    title: str = "Moon, Footprint, Camera, Sun, and Earth",
):
    """Plot Moon/scene geometry with Plotly, Matplotlib, or both."""
    if backend not in {"plotly", "matplotlib", "both"}:
        raise ValueError("backend must be 'plotly', 'matplotlib', or 'both'")

    plotly_figure = None
    matplotlib_figure = None
    if backend in {"plotly", "both"}:
        plotly_target = html_path if html_path is not None else (save_path if backend == "plotly" else _default_html_path(save_path, "_interactive"))
        plotly_figure = _plot_scene_geometry_3d_plotly(
            scene,
            title=title,
            save_path=plotly_target,
            show=show and backend == "plotly",
        )
    if backend in {"matplotlib", "both"}:
        matplotlib_figure = plot_scene_geometry_3d_matplotlib(
            scene,
            save_path=save_path if backend != "plotly" else None,
            title=title,
            show=show,
            block=block,
        )
    return _backend_payload(plotly_figure, matplotlib_figure, backend)


def plot_moon_surface_3d(
    scene,
    *,
    backend: PlotBackend = "plotly",
    show: bool = False,
    save_path: str | Path | None = None,
    html_path: str | Path | None = None,
    block: bool = True,
    title: str = "Moon Surface And Scene Geometry",
):
    """Plot the Moon globe, scene footprint, and space geometry."""
    if backend not in {"plotly", "matplotlib", "both"}:
        raise ValueError("backend must be 'plotly', 'matplotlib', or 'both'")

    plotly_figure = None
    matplotlib_figure = None
    if backend in {"plotly", "both"}:
        plotly_target = html_path if html_path is not None else _default_html_path(save_path, "_moon")
        plotly_figure = _plot_moon_surface_3d_plotly(
            scene,
            title=title,
            save_path=plotly_target,
            show=show and backend == "plotly",
        )
    if backend in {"matplotlib", "both"}:
        matplotlib_figure = _plot_moon_surface_3d_matplotlib(
            scene,
            save_path=save_path if backend != "plotly" else None,
            title=title,
            show=show,
            block=block,
        )
    return _backend_payload(plotly_figure, matplotlib_figure, backend)


def show_landing_site_2d(
    image_or_surface,
    landing_result,
    *,
    backend: PlotBackend = "matplotlib",
    save_path: str | Path | None = None,
    html_path: str | Path | None = None,
    block: bool = True,
    title: str = "Safe Landing Site",
):
    """Show a 2D landing-site overlay."""
    return plot_landing_site_2d(
        image_or_surface,
        landing_result,
        backend=backend,
        show=True,
        save_path=save_path,
        html_path=html_path,
        block=block,
        title=title,
    )


def show_landing_site_3d(
    surface_or_dem,
    landing_result,
    *,
    backend: PlotBackend = "matplotlib",
    save_path: str | Path | None = None,
    html_path: str | Path | None = None,
    block: bool = True,
    title: str = "3D Landing Site Visualization",
):
    """Show a 3D landing-site visualization."""
    return plot_landing_site_3d(
        surface_or_dem,
        landing_result,
        backend=backend,
        show=True,
        save_path=save_path,
        html_path=html_path,
        block=block,
        title=title,
    )


def show_scene_geometry_3d(
    scene,
    *,
    backend: PlotBackend = "matplotlib",
    save_path: str | Path | None = None,
    html_path: str | Path | None = None,
    block: bool = True,
    title: str = "Moon, Footprint, Camera, Sun, and Earth",
):
    """Show Moon/scene geometry."""
    return plot_scene_geometry_3d(
        scene,
        backend=backend,
        show=True,
        save_path=save_path,
        html_path=html_path,
        block=block,
        title=title,
    )


def show_moon_surface_3d(
    scene,
    *,
    backend: PlotBackend = "matplotlib",
    save_path: str | Path | None = None,
    html_path: str | Path | None = None,
    block: bool = True,
    title: str = "Moon Surface And Scene Geometry",
):
    """Show the Moon globe and scene footprint."""
    return plot_moon_surface_3d(
        scene,
        backend=backend,
        show=True,
        save_path=save_path,
        html_path=html_path,
        block=block,
        title=title,
    )


__all__ = [
    "plot_depth_map",
    "show_depth_map",
    "plot_3d_surface",
    "show_surface_3d",
    "plot_3d_surface_interactive",
    "plot_landing_site_2d",
    "show_landing_site_2d",
    "plot_landing_site_3d",
    "show_landing_site_3d",
    "plot_scene_geometry_3d",
    "show_scene_geometry_3d",
    "plot_moon_surface_3d",
    "show_moon_surface_3d",
]
