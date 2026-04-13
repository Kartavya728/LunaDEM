from __future__ import annotations

from pathlib import Path

import numpy as np

from lunadem import (
    TEST_SCENE_ID,
    find_safe_landing_site,
    load_kaguya_scene,
    plot_3d_surface,
    plot_3d_surface_interactive,
    plot_landing_site_2d,
    plot_landing_site_3d,
    plot_moon_surface_3d,
    plot_scene_geometry_3d,
)


def test_surface_plotters_save_outputs(synthetic_image: np.ndarray, tmp_path: Path) -> None:
    png_path = tmp_path / "surface.png"
    html_path = tmp_path / "surface.html"

    figure = plot_3d_surface(synthetic_image, save_path=png_path, show=False)
    interactive = plot_3d_surface_interactive(synthetic_image, save_path=html_path, show=False)

    assert png_path.exists()
    assert html_path.exists()
    assert figure is not None
    assert interactive is not None


def test_landing_and_scene_plotters_support_both_backends(synthetic_image: np.ndarray, tmp_path: Path) -> None:
    landing = find_safe_landing_site(synthetic_image, rover="pragyan", reconstruct=False)
    scene = load_kaguya_scene(TEST_SCENE_ID)

    landing_2d = plot_landing_site_2d(
        synthetic_image,
        landing,
        backend="both",
        show=False,
        save_path=tmp_path / "landing_2d.png",
        html_path=tmp_path / "landing_2d.html",
    )
    landing_3d = plot_landing_site_3d(
        synthetic_image,
        landing,
        backend="both",
        show=False,
        save_path=tmp_path / "landing_3d.png",
        html_path=tmp_path / "landing_3d.html",
    )
    scene_plot = plot_scene_geometry_3d(
        scene,
        backend="both",
        show=False,
        save_path=tmp_path / "scene_geometry.png",
        html_path=tmp_path / "scene_geometry.html",
    )
    moon_plot = plot_moon_surface_3d(
        scene,
        backend="both",
        show=False,
        save_path=tmp_path / "moon_surface.png",
        html_path=tmp_path / "moon_surface.html",
    )

    assert isinstance(landing_2d, dict)
    assert isinstance(landing_3d, dict)
    assert isinstance(scene_plot, dict)
    assert isinstance(moon_plot, dict)
    assert (tmp_path / "landing_2d.png").exists()
    assert (tmp_path / "landing_2d.html").exists()
    assert (tmp_path / "scene_geometry.png").exists()
    assert (tmp_path / "scene_geometry.html").exists()
