from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner
import warnings

import lunadem.cli as cli
from lunadem import __version__
from lunadem.cli import app

runner = CliRunner()


def test_cli_generate_runs(synthetic_image_path: Path, tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "generate",
            str(synthetic_image_path),
            "--method",
            "sfs",
            "--output",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["method"] == "sfs"
    assert payload["exports"]["geotiff"] is not None


def test_cli_analyze_runs(synthetic_image_path: Path, tmp_path: Path) -> None:
    gen = runner.invoke(
        app,
        [
            "generate",
            str(synthetic_image_path),
            "--method",
            "sfs",
            "--output",
            str(tmp_path),
        ],
    )
    assert gen.exit_code == 0
    generated = json.loads(gen.stdout)
    dem_path = generated["exports"]["geotiff"]
    assert dem_path

    analyze = runner.invoke(app, ["analyze", dem_path])
    assert analyze.exit_code == 0
    payload = json.loads(analyze.stdout)
    assert "stats" in payload


def test_lunadem_main_prints_version(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli.sys, "argv", ["lunadem", "--version"])
    cli.lunadem_main()
    assert capsys.readouterr().out.strip() == __version__


def test_lunadem_main_delegates_to_typer_app(monkeypatch) -> None:
    called = {}

    def fake_app(*args, **kwargs):
        called["prog_name"] = kwargs.get("prog_name")

    monkeypatch.setattr(cli, "app", fake_app)
    monkeypatch.setattr(cli.sys, "argv", ["lunadem", "generate", "input.png"])

    cli.lunadem_main()

    assert called["prog_name"] == "lunadem"


def test_sfs_maths_command_runs() -> None:
    result = runner.invoke(app, ["sfs", "--maths"])
    assert result.exit_code == 0
    assert "Lambertian" in result.stdout


def test_download_test_command(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        cli,
        "download_test_scene",
        lambda output_dir, overwrite=False: {"image": str(tmp_path / "image.tif")},
    )
    result = runner.invoke(app, ["download", "--test", "--output", str(tmp_path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["scene_id"]
    assert "image" in payload["downloads"]


def test_lunardem_compatibility_import() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        import lunardem

    assert lunardem.__version__ == __version__
    assert hasattr(lunardem, "generate_dem")
