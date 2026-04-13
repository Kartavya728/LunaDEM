"""Generate API-heavy reference docs from the current lunadem package."""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

import lunadem

ROOT = Path(__file__).resolve().parents[1]
RUN_PATH = ROOT / "run.md"
DOC_PATH = ROOT / "documentation.txt"
METRICS_PATH = ROOT / "lunadem" / "assets" / "models" / "metrics.json"


SPECIAL_EXAMPLES: dict[str, list[str]] = {
    "load_kaguya_scene": [
        "from lunadem import load_kaguya_scene",
        "scene = load_kaguya_scene('TC1S2B0_01_07496N087E3020')",
        "print(scene.scene_id)",
        "print(scene.image_path)",
    ],
    "build_scene_summary": [
        "from lunadem import build_scene_summary, load_kaguya_scene",
        "scene = load_kaguya_scene('TC1S2B0_01_07496N087E3020')",
        "summary = build_scene_summary(scene)",
        "print(summary['centroid'])",
    ],
    "generate_dem": [
        "from lunadem import ReconstructionConfig, generate_dem",
        "config = ReconstructionConfig(output={'output_dir': 'output', 'base_name': 'demo'})",
        "result = generate_dem('dataset/TC1S2B0_01_07496N087E3020/image/image.tif', method='hybrid', config=config)",
        "print(result.dem_meters.shape)",
    ],
    "predict_scene_metadata": [
        "from lunadem import predict_scene_metadata",
        "prediction = predict_scene_metadata('dataset/TC1S2B0_01_07496N087E3020/image/image.tif', max_patches=8)",
        "print(prediction.targets)",
        "print(prediction.patch_count)",
    ],
    "find_safe_landing_site": [
        "from lunadem import find_safe_landing_site, get_rover_spec, load_kaguya_scene",
        "scene = load_kaguya_scene('TC1S2B0_01_07496N087E3020')",
        "landing = find_safe_landing_site(scene.image_path, rover=get_rover_spec('pragyan'), scene=scene)",
        "print(landing.summary)",
    ],
    "plot_scene_geometry_3d": [
        "from lunadem import load_kaguya_scene, plot_scene_geometry_3d",
        "scene = load_kaguya_scene('TC1S2B0_01_07496N087E3020')",
        "figure = plot_scene_geometry_3d(scene, backend='both', show=False, save_path='output/scene_geometry.png', html_path='output/scene_geometry.html')",
        "print(type(figure).__name__)",
    ],
    "plot_moon_surface_3d": [
        "from lunadem import load_kaguya_scene, plot_moon_surface_3d",
        "scene = load_kaguya_scene('TC1S2B0_01_07496N087E3020')",
        "figure = plot_moon_surface_3d(scene, backend='both', show=False, save_path='output/moon_surface.png', html_path='output/moon_surface.html')",
        "print(type(figure).__name__)",
    ],
    "plot_landing_site_2d": [
        "from lunadem import find_safe_landing_site, plot_landing_site_2d, load_kaguya_scene",
        "scene = load_kaguya_scene('TC1S2B0_01_07496N087E3020')",
        "landing = find_safe_landing_site(scene.image_path, scene=scene)",
        "plot_landing_site_2d(scene.image_path, landing, backend='both', show=False, save_path='output/landing_2d.png', html_path='output/landing_2d.html')",
    ],
    "plot_landing_site_3d": [
        "from lunadem import find_safe_landing_site, plot_landing_site_3d, load_kaguya_scene",
        "scene = load_kaguya_scene('TC1S2B0_01_07496N087E3020')",
        "landing = find_safe_landing_site(scene.image_path, scene=scene)",
        "plot_landing_site_3d(scene.image_path, landing, backend='both', show=False, save_path='output/landing_3d.png', html_path='output/landing_3d.html')",
    ],
    "download_test_scene": [
        "from lunadem import download_test_scene",
        "downloads = download_test_scene('downloads', overwrite=False)",
        "print(downloads)",
    ],
}


def _public_symbols() -> list[tuple[str, Any]]:
    names = sorted(set(lunadem.__all__))
    return [(name, getattr(lunadem, name)) for name in names]


def _callable_functions(symbols: list[tuple[str, Any]]) -> list[tuple[str, Any]]:
    functions: list[tuple[str, Any]] = []
    for name, obj in symbols:
        if inspect.isclass(obj):
            continue
        if callable(obj):
            functions.append((name, obj))
    return functions


def _classes(symbols: list[tuple[str, Any]]) -> list[tuple[str, Any]]:
    return [(name, obj) for name, obj in symbols if inspect.isclass(obj)]


def _constants(symbols: list[tuple[str, Any]]) -> list[tuple[str, Any]]:
    return [(name, obj) for name, obj in symbols if not callable(obj)]


def _short_doc(obj: Any) -> str:
    doc = inspect.getdoc(obj) or "No description available."
    return doc.splitlines()[0].strip()


def _signature_text(obj: Any) -> str:
    try:
        return str(inspect.signature(obj))
    except Exception:
        return "(...)"


def _annotation_text(annotation: Any) -> str:
    if annotation is inspect.Signature.empty:
        return "Any"
    return str(annotation).replace("typing.", "")


def _parameter_notes(name: str) -> list[str]:
    lowered = name.lower()
    notes = [f"- `{name}`: user-provided argument."]
    if "image" in lowered:
        notes.append(f"- `{name}` usually accepts a NumPy array or an image/TIFF path.")
    if "dem" in lowered or "surface" in lowered:
        notes.append(f"- `{name}` is typically a height map or terrain-like array.")
    if "scene" in lowered:
        notes.append(f"- `{name}` can often be a scene id, a local scene directory, or a loaded `KaguyaScene`.")
    if "config" in lowered:
        notes.append(f"- `{name}` accepts a typed config model or a compatible mapping.")
    if "save_path" in lowered or lowered.endswith("_path"):
        notes.append(f"- `{name}` should point to a writable path on disk when saving output is desired.")
    if lowered == "backend":
        notes.append("- `backend` should be `matplotlib`, `plotly`, or `both` when the function supports dual rendering.")
    if lowered == "show":
        notes.append("- `show` controls whether a visible window or interactive renderer is opened immediately.")
    return notes


def _generic_example(name: str) -> list[str]:
    return [
        f"from lunadem import {name}",
        f"result = {name}(...)",
        "print(result)",
    ]


def _example_lines(name: str) -> list[str]:
    return SPECIAL_EXAMPLES.get(name, _generic_example(name))


def _metrics_block() -> list[str]:
    payload = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    lines = [
        "Bundled metadata model metrics:",
        f"- Scene count: {payload['scene_count']}",
        f"- Patches per scene: {payload['patches_per_scene']}",
        f"- Package note: {payload.get('note', 'n/a')}",
    ]
    for model_name, model_info in payload["models"].items():
        lines.append(f"- Model: {model_name}")
        lines.append(f"  Targets: {', '.join(model_info['targets'])}")
        for metric_name, metric_value in model_info["metrics"].items():
            lines.append(f"  {metric_name}: {metric_value:.6f}")
    return lines


def _run_md(symbols: list[tuple[str, Any]], functions: list[tuple[str, Any]]) -> str:
    rover_names = ", ".join(lunadem.list_available_rovers())
    scene_names = ", ".join(lunadem.list_kaguya_scenes())
    lines = [
        "# Run Guide For lunadem",
        "",
        "This guide is generated from the installed `lunadem` API surface.",
        "",
        "## Quick Scene",
        "",
        f"- Official test scene: `TC1S2B0_01_07496N087E3020`",
        f"- Local scene folders discovered: `{scene_names}`",
        f"- Built-in rover presets: `{rover_names}`",
        "",
        "## Main CLI Commands",
        "",
        "```bash",
        "lunadem download --test --output downloads",
        "lunadem scene-summary TC1S2B0_01_07496N087E3020",
        "lunadem sfs --maths",
        "lunadem predict dataset/TC1S2B0_01_07496N087E3020/image/image.tif --kind all",
        "lunadem generate dataset/TC1S2B0_01_07496N087E3020/image/image.tif --method hybrid --output output",
        "lunadem plot-surface dataset/TC1S2B0_01_07496N087E3020/image/image.tif --backend both --show --reconstruct",
        "lunadem plot-scene TC1S2B0_01_07496N087E3020 --backend both --show --output output/scene_geometry.png --output-html output/scene_geometry.html",
        "lunadem landing-site dataset/TC1S2B0_01_07496N087E3020/image/image.tif --scene TC1S2B0_01_07496N087E3020 --rover pragyan --backend both --show --output-2d output/landing_2d.png --output-3d output/landing_3d.png --output-2d-html output/landing_2d.html --output-3d-html output/landing_3d.html",
        "```",
        "",
        "## Standard Python Workflow",
        "",
        "```python",
        "from lunadem import (",
        "    build_scene_summary,",
        "    find_safe_landing_site,",
        "    generate_dem,",
        "    get_rover_spec,",
        "    load_kaguya_scene,",
        "    plot_landing_site_2d,",
        "    plot_landing_site_3d,",
        "    plot_moon_surface_3d,",
        "    plot_scene_geometry_3d,",
        "    predict_scene_metadata,",
        ")",
        "",
        "scene = load_kaguya_scene('TC1S2B0_01_07496N087E3020')",
        "summary = build_scene_summary(scene)",
        "prediction = predict_scene_metadata(scene.image_path)",
        "dem = generate_dem(scene.image_path, method='hybrid')",
        "landing = find_safe_landing_site(scene.image_path, rover=get_rover_spec('pragyan'), scene=scene)",
        "plot_scene_geometry_3d(scene, backend='both', show=False, save_path='output/scene_geometry.png', html_path='output/scene_geometry.html')",
        "plot_moon_surface_3d(scene, backend='both', show=False, save_path='output/moon_surface.png', html_path='output/moon_surface.html')",
        "plot_landing_site_2d(scene.image_path, landing, backend='both', show=False, save_path='output/landing_2d.png', html_path='output/landing_2d.html')",
        "plot_landing_site_3d(scene.image_path, landing, backend='both', show=False, save_path='output/landing_3d.png', html_path='output/landing_3d.html')",
        "print(summary['centroid'])",
        "print(prediction.targets)",
        "print(landing.summary)",
        "```",
        "",
        "## Function Catalog",
        "",
        f"The current public API exposes `{len(functions)}` callable functions and helpers. The list below documents more than 30 of them.",
        "",
    ]

    for index, (name, obj) in enumerate(functions, start=1):
        if inspect.isclass(obj):
            continue
        signature = _signature_text(obj)
        lines.extend(
            [
                f"### {index}. `{name}`",
                "",
                f"- Purpose: {_short_doc(obj)}",
                f"- Import: `from lunadem import {name}`",
                f"- Signature: `{name}{signature}`",
                f"- Returns: `{_annotation_text(inspect.signature(obj).return_annotation) if inspect.isroutine(obj) else 'Any'}`",
            ]
        )
        try:
            for parameter_name, parameter in inspect.signature(obj).parameters.items():
                lines.append(f"- Parameter `{parameter_name}`: {_annotation_text(parameter.annotation)}")
        except Exception:
            lines.append("- Parameters: inspect signature not available at runtime.")
        lines.append("- Example:")
        lines.append("```python")
        lines.extend(_example_lines(name))
        lines.append("```")
        lines.append("")

    lines.extend(
        [
            "## Notes",
            "",
            "- Plotting functions support desktop-visible Matplotlib rendering, hoverable Plotly output, or both.",
            "- Metadata prediction functions use bundled ONNX weights and run offline after installation.",
            "- `lunardem` remains import-compatible, but new code should use `lunadem` everywhere.",
        ]
    )
    return "\n".join(lines) + "\n"


def _documentation_txt(symbols: list[tuple[str, Any]], functions: list[tuple[str, Any]], classes: list[tuple[str, Any]], constants: list[tuple[str, Any]]) -> str:
    lines: list[str] = []
    lines.extend(
        [
            "lunadem Documentation",
            "=====================",
            "",
            "This file is generated from the current installed `lunadem` package.",
            "It is intended to be a long-form reference manual for the full public API.",
            "",
            "SECTION 1: INSTALLATION",
            "-----------------------",
            "1. Install the base package with `pip install lunadem`.",
            "2. Install ML extras with `pip install \"lunadem[ml]\"` when retraining or exporting models.",
            "3. Install visualization extras with `pip install \"lunadem[viz]\"` for explicit plotting dependencies.",
            "4. Install development extras with `pip install \"lunadem[dev]\"` when running tests, builds, and release checks.",
            "5. Canonical import name is `lunadem`.",
            "6. Compatibility import `lunardem` still exists but is deprecated.",
            "",
            "SECTION 2: MAJOR CAPABILITIES",
            "-----------------------------",
            "A. DEM generation from image input using shape-from-shading, multi-scale SFS, ML baseline, and hybrid blending.",
            "B. Kaguya scene loading from STAC and camera metadata.",
            "C. Derived lunar geometry helpers for centroid, bbox, sun, camera, transforms, and coverage.",
            "D. Offline metadata prediction from packaged ONNX artifacts.",
            "E. Rover-aware landing-site scoring and visualization.",
            "F. Dual plotting backends with Matplotlib for visible local rendering and Plotly for hoverable 3D output.",
            "G. Reference-scene downloading and packaged theory docs for SFS.",
            "",
            "SECTION 3: CLI REFERENCE",
            "------------------------",
            "Command: lunadem generate",
            "Purpose: reconstruct a DEM from an input image or TIFF.",
            "Command: lunadem analyze",
            "Purpose: compute terrain metrics from an existing DEM.",
            "Command: lunadem landing",
            "Purpose: assess landing safety from an existing DEM.",
            "Command: lunadem scene-summary",
            "Purpose: summarize STAC and camera metadata and derive geometric values.",
            "Command: lunadem predict",
            "Purpose: run the bundled metadata estimators.",
            "Command: lunadem sfs --maths",
            "Purpose: print the SFS mathematics reference.",
            "Command: lunadem sfs --terms",
            "Purpose: print the SFS terminology reference.",
            "Command: lunadem sfs --assumptions",
            "Purpose: print the SFS assumptions reference.",
            "Command: lunadem plot-surface",
            "Purpose: visualize a local terrain surface in 3D.",
            "Command: lunadem plot-scene",
            "Purpose: visualize Moon, footprint, camera, Sun, and Earth geometry.",
            "Command: lunadem landing-site",
            "Purpose: locate the safest rover landing site and plot it.",
            "Command: lunadem download --test",
            "Purpose: download the official packaged test scene.",
            "",
            "SECTION 4: PACKAGED MODEL METRICS",
            "---------------------------------",
        ]
    )
    lines.extend(_metrics_block())
    lines.extend(
        [
            "",
            "SECTION 5: PUBLIC FUNCTION REFERENCE",
            "------------------------------------",
        ]
    )

    for index, (name, obj) in enumerate(functions, start=1):
        signature = _signature_text(obj)
        doc = inspect.getdoc(obj) or "No description available."
        lines.extend(
            [
                f"Function {index}: {name}",
                f"Import: from lunadem import {name}",
                f"Source module: {getattr(obj, '__module__', 'unknown')}",
                f"Signature: {name}{signature}",
                f"Summary: {_short_doc(obj)}",
                "Full docstring:",
            ]
        )
        lines.extend(doc.splitlines() or ["No additional docstring text."])
        lines.append("Parameter details:")
        try:
            signature_obj = inspect.signature(obj)
            if not signature_obj.parameters:
                lines.append("- This callable takes no public parameters.")
            for parameter_name, parameter in signature_obj.parameters.items():
                lines.append(f"- Name: {parameter_name}")
                lines.append(f"  Kind: {parameter.kind}")
                lines.append(f"  Annotation: {_annotation_text(parameter.annotation)}")
                lines.append(f"  Default: {'<required>' if parameter.default is inspect.Signature.empty else parameter.default}")
                lines.extend(_parameter_notes(parameter_name))
        except Exception:
            lines.append("- Signature inspection failed for this callable.")
        lines.append(f"Return annotation: {_annotation_text(getattr(inspect.signature(obj), 'return_annotation', inspect.Signature.empty)) if inspect.isroutine(obj) else 'Any'}")
        lines.append("Usage example:")
        for example_line in _example_lines(name):
            lines.append(f"    {example_line}")
        lines.append("Related notes:")
        lines.append(f"- `{name}` is part of the canonical `lunadem` public API.")
        lines.append("- This symbol is safe to document in `run.md` and example notebooks.")
        lines.append("- Prefer passing typed config models when you want explicit validation.")
        lines.append("- Prefer `show=False` in scripts when generating plots non-interactively.")
        lines.append("- Prefer the packaged test scene for smoke testing before moving to custom data.")
        lines.append("")

    lines.extend(
        [
            "SECTION 6: PUBLIC CLASS REFERENCE",
            "---------------------------------",
        ]
    )
    for index, (name, obj) in enumerate(classes, start=1):
        signature = _signature_text(obj)
        doc = inspect.getdoc(obj) or "No description available."
        lines.extend(
            [
                f"Class {index}: {name}",
                f"Import: from lunadem import {name}",
                f"Source module: {getattr(obj, '__module__', 'unknown')}",
                f"Constructor signature: {name}{signature}",
                f"Summary: {_short_doc(obj)}",
                "Docstring:",
            ]
        )
        lines.extend(doc.splitlines() or ["No additional docstring text."])
        lines.append("Constructor parameters:")
        try:
            signature_obj = inspect.signature(obj)
            if not signature_obj.parameters:
                lines.append("- No explicit constructor parameters were discovered.")
            for parameter_name, parameter in signature_obj.parameters.items():
                lines.append(f"- Name: {parameter_name}")
                lines.append(f"  Annotation: {_annotation_text(parameter.annotation)}")
                lines.append(f"  Default: {'<required>' if parameter.default is inspect.Signature.empty else parameter.default}")
        except Exception:
            lines.append("- Signature inspection failed for this class.")
        lines.append("Example:")
        lines.append(f"    from lunadem import {name}")
        lines.append(f"    instance = {name}(...)")
        lines.append("    print(instance)")
        lines.append("")

    lines.extend(
        [
            "SECTION 7: PUBLIC CONSTANT REFERENCE",
            "------------------------------------",
        ]
    )
    for index, (name, obj) in enumerate(constants, start=1):
        lines.extend(
            [
                f"Constant {index}: {name}",
                f"Import: from lunadem import {name}",
                f"Value preview: {obj}",
                "Note: constants are included here to keep the reference manual complete.",
                "",
            ]
        )

    lines.extend(
        [
            "SECTION 8: RESOURCES AND FILES",
            "-------------------------------",
            f"- README.md path: {ROOT / 'README.md'}",
            f"- run.md path: {RUN_PATH}",
            f"- lunar_data.md path: {ROOT / 'lunar_data.md'}",
            f"- sfs.md path: {ROOT / 'sfs.md'}",
            f"- update.md path: {ROOT / 'update.md'}",
            f"- metrics.json path: {METRICS_PATH}",
            "- Rover reference media under `MISSION CHANDRA/` is used as design context only.",
            "",
            "SECTION 9: TROUBLESHOOTING",
            "--------------------------",
            "- If Matplotlib windows are not desired, set `show=False` and save plots to disk instead.",
            "- If you are running in CI, set `MPLBACKEND=Agg`.",
            "- If model export fails because of ONNX import issues, ensure `ml-dtypes>=0.5` or use the compatibility shim in the training script.",
            "- If large-scene SFS feels slow, reduce `config.sfs.max_long_side_px` further.",
            "- If you only need metadata prediction, call the `predict_*` APIs directly without reconstructing a DEM first.",
            "",
            "SECTION 10: RELEASE CHECKLIST",
            "-----------------------------",
            "1. Run tests.",
            "2. Re-train metadata models when the dataset changes.",
            "3. Re-run this documentation generator.",
            "4. Build wheel and sdist.",
            "5. Verify ONNX artifacts are included.",
            "6. Publish to PyPI and update GitHub release notes.",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    symbols = _public_symbols()
    functions = _callable_functions(symbols)
    classes = _classes(symbols)
    constants = _constants(symbols)

    run_text = _run_md(symbols, functions)
    documentation_text = _documentation_txt(symbols, functions, classes, constants)

    RUN_PATH.write_text(run_text, encoding="utf-8")
    DOC_PATH.write_text(documentation_text, encoding="utf-8")

    line_count = len(documentation_text.splitlines())
    if line_count <= 2000:
        raise RuntimeError(f"documentation.txt is too short: {line_count} lines")

    print(f"Wrote {RUN_PATH.name} with {len(run_text.splitlines())} lines")
    print(f"Wrote {DOC_PATH.name} with {line_count} lines")


if __name__ == "__main__":
    main()
