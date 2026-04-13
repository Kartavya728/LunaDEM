from __future__ import annotations

from pathlib import Path

from lunadem import (
    TEST_SCENE_ID,
    get_model_artifact_paths,
    list_model_names,
    predict_scene_metadata,
)


def test_model_artifacts_exist() -> None:
    paths = get_model_artifact_paths()
    assert sorted(paths) == list_model_names()
    for path in paths.values():
        artifact = Path(path)
        assert artifact.exists()
        assert artifact.suffix == ".onnx"
        assert artifact.stat().st_size > 0


def test_predict_scene_metadata_uses_bundled_models() -> None:
    image_path = Path("dataset") / TEST_SCENE_ID / "image" / "image.tif"
    prediction = predict_scene_metadata(image_path, max_patches=2)

    assert prediction.model_name == "metadata_suite"
    assert prediction.patch_count == 2
    assert "sun_azimuth_deg" in prediction.targets
    assert "centroid_lon_deg" in prediction.targets
