"""Runtime inference for bundled lunar metadata ONNX models."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files
from pathlib import Path
from typing import Any, Dict

import numpy as np
from scipy.ndimage import zoom

from lunadem.core.models import MetadataPrediction
from lunadem.io.image import load_image

MODEL_TARGETS: dict[str, tuple[str, ...]] = {
    "illumination_cnn": ("sun_azimuth_deg", "sun_elevation_deg"),
    "view_geometry_cnn": ("off_nadir_deg", "view_azimuth_deg"),
    "scene_context_cnn": ("gsd_m", "centroid_lat_deg", "centroid_lon_deg"),
}


def _assets_dir() -> Path:
    return Path(files("lunadem")).joinpath("assets", "models")


def list_model_names() -> list[str]:
    """Return the packaged metadata model names."""
    return sorted(MODEL_TARGETS)


def get_model_targets(model_name: str) -> tuple[str, ...]:
    """Return the target names predicted by a given model."""
    if model_name not in MODEL_TARGETS:
        raise KeyError(f"Unknown model {model_name!r}")
    return MODEL_TARGETS[model_name]


def get_model_artifact_paths() -> dict[str, str]:
    """Return the expected packaged ONNX artifact paths."""
    assets_dir = _assets_dir()
    return {name: str(assets_dir / f"{name}.onnx") for name in MODEL_TARGETS}


@lru_cache(maxsize=1)
def get_model_metrics() -> Dict[str, Any]:
    """Load packaged model metrics and scaling metadata."""
    metrics_path = _assets_dir() / "metrics.json"
    if not metrics_path.exists():
        raise FileNotFoundError(
            f"Packaged model metrics not found at {metrics_path}. "
            "Run the metadata training pipeline first."
        )
    return json.loads(metrics_path.read_text(encoding="utf-8"))


@lru_cache(maxsize=8)
def _get_session(model_name: str):
    try:
        import onnxruntime as ort
    except Exception:
        return None
    model_path = _assets_dir() / f"{model_name}.onnx"
    if not model_path.exists():
        return None
    return ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])


def _prepare_patches(
    image_or_tif: np.ndarray | str | Path,
    *,
    patch_size: int,
    max_patches: int,
) -> np.ndarray:
    if isinstance(image_or_tif, np.ndarray):
        image = image_or_tif.astype(np.float32)
    else:
        image, _ = load_image(image_or_tif, normalize=False)
    image = image.astype(np.float32)
    image -= float(np.min(image))
    image /= max(float(np.max(image)), 1e-6)

    if image.shape[0] < patch_size or image.shape[1] < patch_size:
        zoom_factors = (
            max(patch_size / image.shape[0], 1.0),
            max(patch_size / image.shape[1], 1.0),
        )
        image = zoom(image, zoom_factors, order=1).astype(np.float32)

    grid_size = max(1, int(np.ceil(np.sqrt(max_patches))))
    rows = np.linspace(0, max(image.shape[0] - patch_size, 0), num=grid_size, dtype=int)
    cols = np.linspace(0, max(image.shape[1] - patch_size, 0), num=grid_size, dtype=int)

    patches = []
    for row in rows:
        for col in cols:
            patch = image[row : row + patch_size, col : col + patch_size]
            if patch.shape != (patch_size, patch_size):
                continue
            patches.append(patch)
            if len(patches) >= max_patches:
                break
        if len(patches) >= max_patches:
            break

    if not patches:
        patches = [image[:patch_size, :patch_size]]
    return np.stack(patches, axis=0)[:, None, :, :].astype(np.float32)


def _run_model(
    model_name: str,
    image_or_tif: np.ndarray | str | Path,
    *,
    max_patches: int = 16,
) -> MetadataPrediction:
    metrics_payload = get_model_metrics()
    model_info = metrics_payload["models"][model_name]
    session = _get_session(model_name)
    patch_size = int(model_info["patch_size"])
    target_means = np.asarray(model_info["target_mean"], dtype=np.float32)
    target_stds = np.asarray(model_info["target_std"], dtype=np.float32)
    target_names = MODEL_TARGETS[model_name]
    source = str(image_or_tif) if not isinstance(image_or_tif, np.ndarray) else "array_input"

    if session is None:
        return MetadataPrediction(
            model_name=f"{model_name}_fallback",
            targets={name: float(value) for name, value in zip(target_names, target_means)},
            uncertainty={name: float(value) for name, value in zip(target_names, target_stds)},
            metrics=dict(model_info["metrics"]),
            patch_count=0,
            source=source,
        )

    patches = _prepare_patches(image_or_tif, patch_size=patch_size, max_patches=max_patches)
    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: patches})[0]
    outputs = np.asarray(outputs, dtype=np.float32)
    outputs = outputs * target_stds.reshape(1, -1) + target_means.reshape(1, -1)

    targets = {name: float(value) for name, value in zip(target_names, np.mean(outputs, axis=0))}
    uncertainty = {name: float(value) for name, value in zip(target_names, np.std(outputs, axis=0))}
    return MetadataPrediction(
        model_name=model_name,
        targets=targets,
        uncertainty=uncertainty,
        metrics=dict(model_info["metrics"]),
        patch_count=int(outputs.shape[0]),
        source=source,
    )


def predict_illumination(image_or_tif: np.ndarray | str | Path, *, max_patches: int = 16) -> MetadataPrediction:
    """Predict sun azimuth and sun elevation from an image or TIFF."""
    return _run_model("illumination_cnn", image_or_tif, max_patches=max_patches)


def predict_view_geometry(image_or_tif: np.ndarray | str | Path, *, max_patches: int = 16) -> MetadataPrediction:
    """Predict camera view azimuth and off-nadir angle from an image or TIFF."""
    return _run_model("view_geometry_cnn", image_or_tif, max_patches=max_patches)


def predict_scene_location(image_or_tif: np.ndarray | str | Path, *, max_patches: int = 16) -> MetadataPrediction:
    """Predict GSD and approximate scene centroid location from an image or TIFF."""
    return _run_model("scene_context_cnn", image_or_tif, max_patches=max_patches)


def predict_scene_metadata(image_or_tif: np.ndarray | str | Path, *, max_patches: int = 16) -> MetadataPrediction:
    """Run all bundled metadata models and return a merged prediction payload."""
    predictions = [
        predict_illumination(image_or_tif, max_patches=max_patches),
        predict_view_geometry(image_or_tif, max_patches=max_patches),
        predict_scene_location(image_or_tif, max_patches=max_patches),
    ]
    merged_targets: Dict[str, float] = {}
    merged_uncertainty: Dict[str, float] = {}
    merged_metrics: Dict[str, float] = {}
    for prediction in predictions:
        merged_targets.update(prediction.targets)
        merged_uncertainty.update(prediction.uncertainty)
        merged_metrics.update(prediction.metrics)
    return MetadataPrediction(
        model_name="metadata_suite",
        targets=merged_targets,
        uncertainty=merged_uncertainty,
        metrics=merged_metrics,
        patch_count=min(pred.patch_count for pred in predictions),
        source=predictions[0].source,
    )
