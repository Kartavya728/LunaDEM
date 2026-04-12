"""Interactive Plotly-based lunar visualization utilities."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

from lunadem.branding import add_plotly_credit
from lunadem.core.models import KaguyaScene, LandingSiteResult
from lunadem.datasets.kaguya import load_kaguya_scene
from lunadem.geometry.planetary import MOON_RADIUS_M
from lunadem.io.image import load_image


def _save_html(figure: go.Figure, save_path: str | Path | None) -> str | None:
    if save_path is None:
        return None
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pio.write_html(figure, str(path), include_plotlyjs="cdn", auto_open=False)
    return str(path)


def _as_surface(data: np.ndarray | str | Path, normalize: bool = False) -> np.ndarray:
    if isinstance(data, np.ndarray):
        return data.astype(np.float32)
    surface, _ = load_image(data, normalize=normalize)
    return surface.astype(np.float32)


def _downsample(surface: np.ndarray, max_points: int = 200) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    height, width = surface.shape
    stride = max(1, int(max(height, width) / max_points))
    reduced = surface[::stride, ::stride]
    yy, xx = np.indices(reduced.shape)
    return xx * stride, yy * stride, reduced


def plot_3d_surface_interactive(
    surface_or_image: np.ndarray | str | Path,
    *,
    title: str = "Interactive Lunar Surface",
    save_path: str | Path | None = None,
) -> go.Figure:
    """Render a hoverable 3D surface from a DEM or image-like array."""
    surface = _as_surface(surface_or_image)
    xx, yy, zz = _downsample(surface)
    figure = go.Figure(
        data=[
            go.Surface(
                x=xx,
                y=yy,
                z=zz,
                colorscale="Viridis",
                colorbar={"title": "Value"},
                hovertemplate="x=%{x}<br>y=%{y}<br>z=%{z:.3f}<extra></extra>",
            )
        ]
    )
    figure.update_layout(
        title=title,
        scene={"xaxis_title": "Column (px)", "yaxis_title": "Row (px)", "zaxis_title": "Height / intensity"},
        margin={"l": 0, "r": 0, "b": 0, "t": 40},
    )
    add_plotly_credit(figure)
    _save_html(figure, save_path)
    return figure


def plot_landing_site_2d(
    image_or_surface: np.ndarray | str | Path,
    landing_result: LandingSiteResult,
    *,
    title: str = "Safe Landing Site",
    save_path: str | Path | None = None,
) -> go.Figure:
    """Overlay the selected landing site on a 2D image/surface view."""
    image = _as_surface(image_or_surface, normalize=False)
    mask = landing_result.safe_mask.astype(np.float32)
    figure = go.Figure()
    figure.add_trace(go.Heatmap(z=image, colorscale="Gray", showscale=False, hovertemplate="value=%{z:.3f}<extra></extra>"))
    figure.add_trace(
        go.Contour(
            z=mask,
            contours={"start": 0.5, "end": 0.5, "size": 1.0},
            line={"color": "lime", "width": 2},
            showscale=False,
            hoverinfo="skip",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=[landing_result.col],
            y=[landing_result.row],
            mode="markers",
            marker={"color": "red", "size": 10, "symbol": "x"},
            name="Best landing site",
        )
    )
    figure.update_layout(title=title, xaxis_title="Column (px)", yaxis_title="Row (px)", yaxis={"autorange": "reversed"})
    add_plotly_credit(figure)
    _save_html(figure, save_path)
    return figure


def _add_rover_box(figure: go.Figure, x_center: float, y_center: float, z_center: float, length: float, width: float, height: float) -> None:
    x0, x1 = x_center - length / 2.0, x_center + length / 2.0
    y0, y1 = y_center - width / 2.0, y_center + width / 2.0
    z0, z1 = z_center, z_center + height
    vertices = np.array(
        [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]],
        dtype=np.float64,
    )
    i = [0, 0, 0, 1, 1, 2, 4, 4, 5, 6, 2, 3]
    j = [1, 2, 4, 2, 5, 3, 5, 6, 6, 7, 6, 7]
    k = [2, 4, 5, 5, 6, 7, 6, 7, 7, 4, 3, 4]
    figure.add_trace(go.Mesh3d(x=vertices[:, 0], y=vertices[:, 1], z=vertices[:, 2], i=i, j=j, k=k, color="orange", opacity=0.5, name="Rover", hoverinfo="skip"))


def plot_landing_site_3d(
    surface_or_dem: np.ndarray | str | Path,
    landing_result: LandingSiteResult,
    *,
    title: str = "3D Landing Site Visualization",
    save_path: str | Path | None = None,
) -> go.Figure:
    """Render the landing site on an interactive 3D surface with rover box."""
    surface = _as_surface(surface_or_dem)
    xx, yy, zz = _downsample(surface)
    row = max(min(landing_result.row, surface.shape[0] - 1), 0)
    col = max(min(landing_result.col, surface.shape[1] - 1), 0)
    z_value = float(surface[row, col])

    figure = go.Figure(data=[go.Surface(x=xx, y=yy, z=zz, colorscale="Earth", opacity=0.95, hovertemplate="x=%{x}<br>y=%{y}<br>z=%{z:.3f}<extra></extra>")])
    figure.add_trace(go.Scatter3d(x=[col], y=[row], z=[z_value], mode="markers", marker={"size": 6, "color": "red"}, name="Best landing site"))

    rover = landing_result.rover
    px_to_m = max(landing_result.pixel_size_m, 1e-6)
    _add_rover_box(figure, x_center=col, y_center=row, z_center=z_value, length=rover.length_m / px_to_m, width=rover.width_m / px_to_m, height=max(rover.height_m / px_to_m, 1.0))

    figure.update_layout(
        title=title,
        scene={"xaxis_title": "Column (px)", "yaxis_title": "Row (px)", "zaxis_title": "Height / intensity"},
        margin={"l": 0, "r": 0, "b": 0, "t": 40},
    )
    add_plotly_credit(figure)
    _save_html(figure, save_path)
    return figure


def plot_scene_geometry_3d(
    scene: KaguyaScene | str | Path,
    *,
    title: str = "Moon, Footprint, Camera, Sun, and Earth",
    save_path: str | Path | None = None,
) -> go.Figure:
    """Render the Moon, scene footprint, and space-geometry vectors."""
    resolved_scene = scene if isinstance(scene, KaguyaScene) else load_kaguya_scene(scene)
    geometry = resolved_scene.geometry
    moon_radius_km = MOON_RADIUS_M / 1_000.0

    u = np.linspace(0, 2 * np.pi, 48)
    v = np.linspace(0, np.pi, 24)
    x = moon_radius_km * np.outer(np.cos(u), np.sin(v))
    y = moon_radius_km * np.outer(np.sin(u), np.sin(v))
    z = moon_radius_km * np.outer(np.ones_like(u), np.cos(v))

    figure = go.Figure()
    figure.add_trace(go.Surface(x=x, y=y, z=z, colorscale=[[0.0, "#5f5f5f"], [1.0, "#d9d9d9"]], opacity=0.75, showscale=False, name="Moon", hoverinfo="skip"))

    if geometry.footprint_xyz_m:
        coords = np.asarray(geometry.footprint_xyz_m, dtype=np.float64) / 1_000.0
        figure.add_trace(go.Scatter3d(x=coords[:, 0], y=coords[:, 1], z=coords[:, 2], mode="lines", line={"color": "cyan", "width": 5}, name="Scene footprint"))

    if geometry.mean_camera_position_km is not None:
        camera = geometry.mean_camera_position_km
        figure.add_trace(go.Scatter3d(x=[camera[0]], y=[camera[1]], z=[camera[2]], mode="markers", marker={"color": "orange", "size": 6}, name="Camera"))

    if geometry.mean_sun_position_km is not None:
        sun_dir = np.asarray(geometry.mean_sun_position_km, dtype=np.float64)
        sun_dir = sun_dir / max(np.linalg.norm(sun_dir), 1e-6)
        sun = sun_dir * moon_radius_km * 8.0
        figure.add_trace(go.Scatter3d(x=[sun[0]], y=[sun[1]], z=[sun[2]], mode="markers", marker={"color": "yellow", "size": 8}, name="Sun direction"))

    if geometry.footprint_xyz_m:
        footprint_center = np.asarray(geometry.footprint_xyz_m[0], dtype=np.float64) / 1_000.0
        earth_dir = footprint_center / max(np.linalg.norm(footprint_center), 1e-6)
        earth = earth_dir * 384_400.0
        figure.add_trace(go.Scatter3d(x=[earth[0]], y=[earth[1]], z=[earth[2]], mode="markers", marker={"color": "blue", "size": 7}, name="Earth (approx.)"))

    figure.update_layout(
        title=title,
        scene={"xaxis_title": "X (km)", "yaxis_title": "Y (km)", "zaxis_title": "Z (km)", "aspectmode": "data"},
        margin={"l": 0, "r": 0, "b": 0, "t": 40},
    )
    add_plotly_credit(figure)
    _save_html(figure, save_path)
    return figure
