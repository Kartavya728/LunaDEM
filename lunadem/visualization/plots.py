"""Matplotlib-based plotting utilities for lunadem."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib
import numpy as np

from lunadem.branding import add_matplotlib_credit
from lunadem.core.models import KaguyaScene, LandingSiteResult
from lunadem.datasets.kaguya import load_kaguya_scene
from lunadem.geometry.planetary import MOON_RADIUS_M
from lunadem.io.image import load_image


def _get_pyplot(show: bool):
    if not show:
        try:
            matplotlib.use("Agg")
        except Exception:
            pass
    import matplotlib.pyplot as plt

    return plt


def _save_figure(fig: Any, save_path: str | Path | None) -> str | None:
    if save_path is None:
        return None
    out = Path(save_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    return str(out)


def _finalize_figure(fig: Any, *, save_path: str | Path | None, show: bool, block: bool) -> Any:
    _save_figure(fig, save_path)
    if show:
        plt = _get_pyplot(True)
        plt.show(block=block)
    else:
        plt = _get_pyplot(False)
        plt.close(fig)
    return fig


def _as_surface_array(surface_or_image: np.ndarray | str | Path, normalize: bool = False) -> np.ndarray:
    if isinstance(surface_or_image, np.ndarray):
        return surface_or_image.astype(np.float32)
    surface, _ = load_image(surface_or_image, normalize=normalize)
    return surface.astype(np.float32)


def _downsample(surface: np.ndarray, max_points: int = 200) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    height, width = surface.shape
    stride = max(1, int(max(height, width) / max_points))
    reduced = surface[::stride, ::stride]
    yy, xx = np.indices(reduced.shape)
    return xx * stride, yy * stride, reduced


def plot_depth_map(
    dem: np.ndarray,
    save_path: str | Path | None = None,
    *,
    title: str = "Reconstructed DEM",
    show: bool = False,
    block: bool = True,
):
    """Render a 2D terrain map with Matplotlib."""
    plt = _get_pyplot(show)
    dem = dem.astype(np.float32)
    fig, ax = plt.subplots(figsize=(10, 8))
    image = ax.imshow(dem, cmap="terrain")
    ax.set_title(title)
    ax.set_xlabel("X (pixels)")
    ax.set_ylabel("Y (pixels)")
    cbar = fig.colorbar(image, ax=ax)
    cbar.set_label("Height (m)")
    add_matplotlib_credit(fig)
    fig.tight_layout()
    return _finalize_figure(fig, save_path=save_path, show=show, block=block)


def show_depth_map(
    dem: np.ndarray,
    save_path: str | Path | None = None,
    *,
    title: str = "Reconstructed DEM",
    block: bool = True,
):
    """Show a 2D terrain map using Matplotlib."""
    return plot_depth_map(dem, save_path=save_path, title=title, show=True, block=block)


def plot_3d_surface(
    dem: np.ndarray,
    save_path: str | Path | None = None,
    *,
    title: str = "Reconstructed 3D Surface",
    show: bool = False,
    block: bool = True,
    max_points: int = 200,
):
    """Render a 3D terrain surface with Matplotlib."""
    plt = _get_pyplot(show)
    dem = dem.astype(np.float32)
    xx, yy, zz = _downsample(dem, max_points=max_points)
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(
        xx,
        yy,
        zz,
        cmap="terrain",
        linewidth=0,
        antialiased=False,
    )
    ax.set_title(title)
    ax.set_xlabel("X (pixels)")
    ax.set_ylabel("Y (pixels)")
    ax.set_zlabel("Height (m)")
    ax.set_box_aspect((max(xx.max(), 1), max(yy.max(), 1), max(float(np.ptp(zz)), 1.0)))
    fig.colorbar(surf, shrink=0.6, aspect=10, label="Height (m)")
    add_matplotlib_credit(fig)
    fig.tight_layout()
    return _finalize_figure(fig, save_path=save_path, show=show, block=block)


def show_surface_3d(
    dem: np.ndarray,
    save_path: str | Path | None = None,
    *,
    title: str = "Reconstructed 3D Surface",
    block: bool = True,
    max_points: int = 200,
):
    """Show a 3D terrain surface using Matplotlib."""
    return plot_3d_surface(dem, save_path=save_path, title=title, show=True, block=block, max_points=max_points)


def plot_landing_site_2d_matplotlib(
    image_or_surface: np.ndarray | str | Path,
    landing_result: LandingSiteResult,
    save_path: str | Path | None = None,
    *,
    title: str = "Safe Landing Site",
    show: bool = False,
    block: bool = True,
):
    """Plot the safe landing site overlay using Matplotlib."""
    plt = _get_pyplot(show)
    image = _as_surface_array(image_or_surface, normalize=False)
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(image, cmap="gray")
    ax.contour(landing_result.safe_mask.astype(np.float32), levels=[0.5], colors=["lime"], linewidths=1.5)
    ax.scatter([landing_result.col], [landing_result.row], c="red", marker="x", s=80, label="Best landing site")
    ax.set_title(title)
    ax.set_xlabel("Column (px)")
    ax.set_ylabel("Row (px)")
    ax.legend(loc="upper right")
    add_matplotlib_credit(fig)
    fig.tight_layout()
    return _finalize_figure(fig, save_path=save_path, show=show, block=block)


def show_landing_site_2d(
    image_or_surface: np.ndarray | str | Path,
    landing_result: LandingSiteResult,
    save_path: str | Path | None = None,
    *,
    title: str = "Safe Landing Site",
    block: bool = True,
):
    """Show the safe landing site overlay using Matplotlib."""
    return plot_landing_site_2d_matplotlib(
        image_or_surface,
        landing_result,
        save_path=save_path,
        title=title,
        show=True,
        block=block,
    )


def plot_landing_site_3d_matplotlib(
    surface_or_dem: np.ndarray | str | Path,
    landing_result: LandingSiteResult,
    save_path: str | Path | None = None,
    *,
    title: str = "3D Landing Site Visualization",
    show: bool = False,
    block: bool = True,
    max_points: int = 200,
):
    """Render a landing site on a Matplotlib 3D terrain surface."""
    plt = _get_pyplot(show)
    surface = _as_surface_array(surface_or_dem, normalize=False)
    xx, yy, zz = _downsample(surface, max_points=max_points)
    row = min(max(landing_result.row, 0), surface.shape[0] - 1)
    col = min(max(landing_result.col, 0), surface.shape[1] - 1)
    z_value = float(surface[row, col])

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(xx, yy, zz, cmap="terrain", linewidth=0, antialiased=False, alpha=0.95)
    ax.scatter([col], [row], [z_value], c="red", s=60, marker="x")

    half_length = landing_result.rover.length_m / max(landing_result.pixel_size_m, 1e-6) / 2.0
    half_width = landing_result.rover.width_m / max(landing_result.pixel_size_m, 1e-6) / 2.0
    rover_height = max(landing_result.rover.height_m / max(landing_result.pixel_size_m, 1e-6), 1.0)
    ax.bar3d(
        col - half_length,
        row - half_width,
        z_value,
        2.0 * half_length,
        2.0 * half_width,
        rover_height,
        shade=True,
        color="orange",
        alpha=0.45,
    )

    ax.set_title(title)
    ax.set_xlabel("Column (px)")
    ax.set_ylabel("Row (px)")
    ax.set_zlabel("Height / intensity")
    add_matplotlib_credit(fig)
    fig.tight_layout()
    return _finalize_figure(fig, save_path=save_path, show=show, block=block)


def show_landing_site_3d(
    surface_or_dem: np.ndarray | str | Path,
    landing_result: LandingSiteResult,
    save_path: str | Path | None = None,
    *,
    title: str = "3D Landing Site Visualization",
    block: bool = True,
    max_points: int = 200,
):
    """Show the landing site on a Matplotlib 3D terrain surface."""
    return plot_landing_site_3d_matplotlib(
        surface_or_dem,
        landing_result,
        save_path=save_path,
        title=title,
        show=True,
        block=block,
        max_points=max_points,
    )


def plot_scene_geometry_3d_matplotlib(
    scene: KaguyaScene | str | Path,
    save_path: str | Path | None = None,
    *,
    title: str = "Moon, Footprint, Camera, Sun, and Earth",
    show: bool = False,
    block: bool = True,
):
    """Render Moon, footprint, camera, Sun, and Earth using Matplotlib."""
    plt = _get_pyplot(show)
    resolved_scene = scene if isinstance(scene, KaguyaScene) else load_kaguya_scene(scene)
    geometry = resolved_scene.geometry
    moon_radius_km = MOON_RADIUS_M / 1_000.0

    u = np.linspace(0, 2.0 * np.pi, 64)
    v = np.linspace(0, np.pi, 32)
    x = moon_radius_km * np.outer(np.cos(u), np.sin(v))
    y = moon_radius_km * np.outer(np.sin(u), np.sin(v))
    z = moon_radius_km * np.outer(np.ones_like(u), np.cos(v))

    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(x, y, z, color="#bcbcbc", alpha=0.35, linewidth=0, antialiased=False)

    if geometry.footprint_xyz_m:
        coords = np.asarray(geometry.footprint_xyz_m, dtype=np.float64) / 1_000.0
        ax.plot(coords[:, 0], coords[:, 1], coords[:, 2], color="cyan", linewidth=2.0, label="Scene footprint")

    if geometry.mean_camera_position_km is not None:
        camera = np.asarray(geometry.mean_camera_position_km, dtype=np.float64)
        ax.scatter([camera[0]], [camera[1]], [camera[2]], c="orange", s=50, label="Camera")

    if geometry.mean_sun_position_km is not None:
        sun_dir = np.asarray(geometry.mean_sun_position_km, dtype=np.float64)
        sun_dir = sun_dir / max(np.linalg.norm(sun_dir), 1e-6)
        sun = sun_dir * moon_radius_km * 8.0
        ax.scatter([sun[0]], [sun[1]], [sun[2]], c="gold", s=70, label="Sun direction")

    if geometry.footprint_xyz_m:
        footprint_center = np.asarray(geometry.footprint_xyz_m[0], dtype=np.float64) / 1_000.0
        earth_dir = footprint_center / max(np.linalg.norm(footprint_center), 1e-6)
        earth = earth_dir * 384_400.0
        ax.scatter([earth[0]], [earth[1]], [earth[2]], c="royalblue", s=60, label="Earth (approx.)")

    ax.set_title(title)
    ax.set_xlabel("X (km)")
    ax.set_ylabel("Y (km)")
    ax.set_zlabel("Z (km)")
    ax.legend(loc="upper left")
    add_matplotlib_credit(fig)
    fig.tight_layout()
    return _finalize_figure(fig, save_path=save_path, show=show, block=block)


def plot_moon_surface_3d(
    scene: KaguyaScene | str | Path,
    save_path: str | Path | None = None,
    *,
    title: str = "Moon Surface And Scene Geometry",
    show: bool = False,
    block: bool = True,
):
    """Render the Moon globe and scene footprint using Matplotlib."""
    return plot_scene_geometry_3d_matplotlib(
        scene,
        save_path=save_path,
        title=title,
        show=show,
        block=block,
    )


def show_moon_surface_3d(
    scene: KaguyaScene | str | Path,
    save_path: str | Path | None = None,
    *,
    title: str = "Moon Surface And Scene Geometry",
    block: bool = True,
):
    """Show the Moon globe and scene footprint using Matplotlib."""
    return plot_moon_surface_3d(scene, save_path=save_path, title=title, show=True, block=block)


def show_scene_geometry_3d(
    scene: KaguyaScene | str | Path,
    save_path: str | Path | None = None,
    *,
    title: str = "Moon, Footprint, Camera, Sun, and Earth",
    block: bool = True,
):
    """Show Moon, footprint, camera, Sun, and Earth using Matplotlib."""
    return plot_scene_geometry_3d_matplotlib(
        scene,
        save_path=save_path,
        title=title,
        show=True,
        block=block,
    )
