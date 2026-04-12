from __future__ import annotations

from lunadem import TEST_SCENE_ID, get_test_scene_manifest, load_camera_model, load_stac_item, summarize_scene_metadata


def test_load_stac_item_reads_local_scene() -> None:
    item = load_stac_item(TEST_SCENE_ID)
    assert item["id"] == TEST_SCENE_ID
    assert "properties" in item


def test_load_camera_model_reads_local_scene() -> None:
    camera = load_camera_model(TEST_SCENE_ID)
    assert "instrument_position" in camera
    assert "sun_position" in camera


def test_summarize_scene_metadata_derives_geometry() -> None:
    item = load_stac_item(TEST_SCENE_ID)
    camera = load_camera_model(TEST_SCENE_ID)
    geometry = summarize_scene_metadata(item, camera)
    assert geometry.gsd_m is not None
    assert geometry.acquisition_duration_s is not None
    assert geometry.line_time_s is not None
    assert geometry.mean_camera_distance_km is not None


def test_get_test_scene_manifest_matches_reference_scene() -> None:
    manifest = get_test_scene_manifest()
    assert manifest["scene_id"] == TEST_SCENE_ID
    assert "image" in manifest["assets"]
