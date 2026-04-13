from __future__ import annotations

import lunadem


def test_top_level_imports_include_runtime_entrypoints() -> None:
    assert callable(lunadem.find_safe_landing_site)
    assert callable(lunadem.generate_dem)
    assert callable(lunadem.predict_scene_metadata)
    assert callable(lunadem.plot_scene_geometry_3d)
    assert callable(lunadem.plot_moon_surface_3d)


def test_public_api_has_more_than_40_callable_symbols() -> None:
    callable_symbols = [
        name
        for name in dir(lunadem)
        if not name.startswith("_") and callable(getattr(lunadem, name))
    ]
    assert len(callable_symbols) >= 40


def test_scene_summary_helpers_work_on_reference_scene() -> None:
    scene = lunadem.load_kaguya_scene(lunadem.TEST_SCENE_ID)
    summary = lunadem.build_scene_summary(scene)

    assert summary["scene_id"] == lunadem.TEST_SCENE_ID
    assert "geometry" in summary
    assert "camera" in summary
    assert "sun" in summary
    assert lunadem.get_scene_centroid(scene)[0] is not None
