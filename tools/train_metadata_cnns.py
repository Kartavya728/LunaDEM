"""Train lightweight metadata CNNs from the local Kaguya dataset and export ONNX models."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import rasterio
import torch
import torch.nn as nn
from sklearn.model_selection import GroupKFold
from torch.utils.data import DataLoader, TensorDataset

from lunadem.datasets.kaguya import DEFAULT_DATASET_ROOT, load_kaguya_scene

SEED = 42
PATCH_SIZE = 96
PATCHES_PER_SCENE = 16
EPOCHS = 10
BATCH_SIZE = 32
DEVICE = torch.device("cpu")

MODEL_SPECS = {
    "illumination_cnn": {
        "targets": ("sun_azimuth_deg", "sun_elevation_deg"),
    },
    "view_geometry_cnn": {
        "targets": ("off_nadir_deg", "view_azimuth_deg"),
    },
    "scene_context_cnn": {
        "targets": ("gsd_m", "centroid_lat_deg", "centroid_lon_deg"),
    },
}


@dataclass
class SceneRecord:
    scene_id: str
    image_path: Path
    labels: dict[str, float]


class TinyMetaCNN(nn.Module):
    """Compact CNN used for metadata regression."""

    def __init__(self, output_dim: int) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 8, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(8, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
        )
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(32, 32),
            nn.ReLU(),
            nn.Linear(32, output_dim),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.head(self.features(inputs))


def _patch_ml_dtypes_for_onnx() -> None:
    """Patch older ml_dtypes installs so ONNX import/export remains usable."""
    try:
        import ml_dtypes
    except Exception:
        return

    alias_map = {
        "float4_e2m1fn": "float8_e4m3fn",
        "float4_e2m1fnuz": "float8_e4m3fnuz",
        "float8_e8m0fnu": "float8_e5m2",
    }
    for missing_name, fallback_name in alias_map.items():
        if not hasattr(ml_dtypes, missing_name) and hasattr(ml_dtypes, fallback_name):
            setattr(ml_dtypes, missing_name, getattr(ml_dtypes, fallback_name))


def _set_seed(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def _scene_records(dataset_root: Path) -> list[SceneRecord]:
    records: list[SceneRecord] = []
    for scene_dir in sorted(dataset_root.iterdir()):
        if not scene_dir.is_dir():
            continue
        scene = load_kaguya_scene(scene_dir)
        records.append(
            SceneRecord(
                scene_id=scene.scene_id,
                image_path=scene.image_path,
                labels={
                    "sun_azimuth_deg": float(scene.stac_item["properties"]["view:sun_azimuth"]),
                    "sun_elevation_deg": float(scene.stac_item["properties"]["view:sun_elevation"]),
                    "off_nadir_deg": float(scene.stac_item["properties"]["view:off_nadir"]),
                    "view_azimuth_deg": float(scene.stac_item["properties"]["view:azimuth"]),
                    "gsd_m": float(scene.stac_item["properties"]["gsd"]),
                    "centroid_lat_deg": float(scene.stac_item["properties"]["proj:centroid"]["lat"]),
                    "centroid_lon_deg": float(scene.stac_item["properties"]["proj:centroid"]["lon"]),
                },
            )
        )
    return records


def _sample_patches(image_path: Path, patch_size: int, patches_per_scene: int, rng: np.random.Generator) -> np.ndarray:
    with rasterio.open(image_path) as src:
        band = src.read(1).astype(np.float32)
    band -= float(np.min(band))
    band /= max(float(np.max(band)), 1e-6)

    patches = []
    max_row = max(band.shape[0] - patch_size, 1)
    max_col = max(band.shape[1] - patch_size, 1)
    for _ in range(patches_per_scene):
        row = int(rng.integers(0, max_row))
        col = int(rng.integers(0, max_col))
        patch = band[row : row + patch_size, col : col + patch_size]
        if patch.shape == (patch_size, patch_size):
            patches.append(patch)
    return np.stack(patches, axis=0).astype(np.float32)


def _build_dataset(records: Iterable[SceneRecord]) -> tuple[np.ndarray, dict[str, np.ndarray], np.ndarray]:
    rng = np.random.default_rng(SEED)
    patch_list = []
    groups = []
    labels_by_name = {target: [] for spec in MODEL_SPECS.values() for target in spec["targets"]}

    for scene_index, record in enumerate(records):
        patches = _sample_patches(record.image_path, PATCH_SIZE, PATCHES_PER_SCENE, rng)
        patch_list.append(patches[:, None, :, :])
        groups.extend([scene_index] * len(patches))
        for target_name in labels_by_name:
            labels_by_name[target_name].extend([record.labels[target_name]] * len(patches))

    x = np.concatenate(patch_list, axis=0)
    y = {key: np.asarray(values, dtype=np.float32) for key, values in labels_by_name.items()}
    return x, y, np.asarray(groups, dtype=np.int64)


def _train_model(x_train: np.ndarray, y_train: np.ndarray, output_dim: int) -> TinyMetaCNN:
    model = TinyMetaCNN(output_dim=output_dim).to(DEVICE)
    dataset = TensorDataset(torch.from_numpy(x_train), torch.from_numpy(y_train))
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()

    model.train()
    for _ in range(EPOCHS):
        for inputs, targets in loader:
            inputs = inputs.to(DEVICE)
            targets = targets.to(DEVICE)
            optimizer.zero_grad()
            predictions = model(inputs)
            loss = loss_fn(predictions, targets)
            loss.backward()
            optimizer.step()
    return model


def _predict(model: TinyMetaCNN, x: np.ndarray) -> np.ndarray:
    model.eval()
    with torch.no_grad():
        predictions = model(torch.from_numpy(x).to(DEVICE)).cpu().numpy()
    return predictions.astype(np.float32)


def _scene_level_mean(values: np.ndarray, groups: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    unique_groups = np.unique(groups)
    means = []
    ordered_groups = []
    for group in unique_groups:
        mask = groups == group
        means.append(np.mean(values[mask], axis=0))
        ordered_groups.append(group)
    return np.asarray(means, dtype=np.float32), np.asarray(ordered_groups, dtype=np.int64)


def main() -> None:
    _set_seed()
    _patch_ml_dtypes_for_onnx()
    import onnx  # noqa: F401

    dataset_root = Path(DEFAULT_DATASET_ROOT)
    output_root = Path("lunadem") / "assets" / "models"
    output_root.mkdir(parents=True, exist_ok=True)

    records = _scene_records(dataset_root)
    x, labels_by_name, groups = _build_dataset(records)

    metrics_payload = {
        "models": {},
        "scene_count": len(records),
        "patches_per_scene": PATCHES_PER_SCENE,
        "note": "real_onnx_models",
    }
    group_kfold = GroupKFold(n_splits=min(3, len(records)))

    for model_name, spec in MODEL_SPECS.items():
        target_names = spec["targets"]
        y = np.stack([labels_by_name[target_name] for target_name in target_names], axis=1)
        fold_errors = []

        for train_index, test_index in group_kfold.split(x, y, groups=groups):
            y_train = y[train_index]
            target_mean = np.mean(y_train, axis=0, keepdims=True)
            target_std = np.std(y_train, axis=0, keepdims=True) + 1e-6

            model = _train_model(
                x[train_index],
                ((y_train - target_mean) / target_std).astype(np.float32),
                output_dim=y.shape[1],
            )
            predictions = _predict(model, x[test_index]) * target_std + target_mean
            pred_scene, pred_groups = _scene_level_mean(predictions, groups[test_index])
            truth_scene, _ = _scene_level_mean(y[test_index], groups[test_index])
            _ = pred_groups
            fold_errors.append(np.mean(np.abs(pred_scene - truth_scene), axis=0))

        fold_errors_np = np.asarray(fold_errors, dtype=np.float32)
        mean_errors = np.mean(fold_errors_np, axis=0)

        full_mean = np.mean(y, axis=0, keepdims=True)
        full_std = np.std(y, axis=0, keepdims=True) + 1e-6
        final_model = _train_model(x, ((y - full_mean) / full_std).astype(np.float32), output_dim=y.shape[1])

        dummy = torch.from_numpy(x[:1]).to(DEVICE)
        torch.onnx.export(
            final_model,
            dummy,
            output_root / f"{model_name}.onnx",
            input_names=["input"],
            output_names=["output"],
            dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}},
            opset_version=17,
        )

        metrics_payload["models"][model_name] = {
            "targets": list(target_names),
            "target_mean": full_mean.ravel().tolist(),
            "target_std": full_std.ravel().tolist(),
            "patch_size": PATCH_SIZE,
            "metrics": {
                f"{target_name}_mae": float(error)
                for target_name, error in zip(target_names, mean_errors)
            },
        }

    (output_root / "metrics.json").write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")
    print(json.dumps(metrics_payload, indent=2))


if __name__ == "__main__":
    main()
