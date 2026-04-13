from __future__ import annotations

from lunadem import ReconstructionConfig, generate_dem, load_kaguya_scene


def test_large_scene_generation_uses_working_resolution() -> None:
    scene = load_kaguya_scene("TC1S2B0_01_07496N087E3020")
    config = ReconstructionConfig(
        output={
            "output_dir": "output",
            "base_name": "large_scene_test",
            "save_geotiff": False,
            "save_obj": False,
            "save_ply": False,
            "save_visualizations": False,
            "save_interactive_html": False,
            "save_manifest": False,
        },
        sfs={
            "max_iterations": 4,
            "max_long_side_px": 384,
        },
    )

    result = generate_dem(scene.image_path, method="hybrid", config=config)

    assert result.dem_meters.shape[0] > 1000
    assert result.dem_meters.shape[1] > 1000
    assert result.diagnostics["sfs"]["used_working_resolution"] is True
    assert result.diagnostics["sfs"]["working_height"] <= 384
    assert result.diagnostics["sfs"]["working_width"] <= 384
