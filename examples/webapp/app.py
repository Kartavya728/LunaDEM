"""Deprecated Flask demo app.

This app is intentionally lightweight and kept under examples.
Library users should prefer the Python API or CLI.
"""

from __future__ import annotations

from flask import Flask, jsonify, request

from lunardem import ReconstructionConfig, generate_dem

app = Flask(__name__)


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok", "message": "LunarDEM example web app"}


@app.post("/generate")
def generate() -> tuple[dict[str, object], int]:
    if "image_file" not in request.files:
        return {"error": "image_file is required"}, 400

    file = request.files["image_file"]
    if not file.filename:
        return {"error": "Invalid filename"}, 400

    temp_path = f"uploads/{file.filename}"
    file.save(temp_path)

    config = ReconstructionConfig(
        output={"output_dir": "output", "base_name": "webapp_run"},
    )
    result = generate_dem(temp_path, method="sfs", config=config)
    payload = {
        "exports": result.exports,
        "diagnostics": result.diagnostics,
        "stats": result.metrics.stats if result.metrics else {},
    }
    return jsonify(payload), 200


if __name__ == "__main__":
    app.run(debug=True)
