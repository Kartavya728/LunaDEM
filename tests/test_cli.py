from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from lunardem.cli import app

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
