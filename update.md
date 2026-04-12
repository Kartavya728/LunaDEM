# lunadem Release Guide

This guide covers pushing the new `lunadem` codebase to both GitHub and PyPI.

## Version Source

The canonical package version is stored in:

- `lunadem/__init__.py`

Current version in this branch:

- `0.3.0`

## 1. Verify The Canonical Package Name

Before building, confirm these points:

- Python import name: `lunadem`
- Primary CLI: `lunadem`
- Compatibility alias: `lunardem`

## 2. Run Local Checks

Use a healthy Python environment before release.

```powershell
python -m pytest
python -m build
python -m twine check dist/*
```

If you want to regenerate metadata model exports:

```powershell
python tools/train_metadata_cnns.py
```

## 3. Clean Old Artifacts

```powershell
if (Test-Path dist) { Remove-Item -Recurse -Force dist }
if (Test-Path build) { Remove-Item -Recurse -Force build }
Get-ChildItem -Recurse -Directory -Filter "*.egg-info" | Remove-Item -Recurse -Force
```

## 4. Build Wheels And Source Distribution

The project now uses `scikit-build-core` and an optional pybind11 extension.

```powershell
python -m build
```

Important:

- If a compiler is available, the native `_native` module will be built.
- If not, the Python fallbacks still keep the library usable.

## 5. Upload To TestPyPI First

```powershell
python -m twine upload --repository testpypi dist/*
```

Then verify installation in a clean environment:

```powershell
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple --no-cache-dir lunadem==0.3.0
lunadem --help
lunadem sfs --maths
lunadem scene-summary TC1S2B0_01_07496N087E3020
```

## 6. Upload To Production PyPI

```powershell
python -m twine upload dist/*
```

## 7. Push To GitHub

Commit the release branch and push:

```powershell
git add .
git commit -m "Release lunadem 0.3.0"
git push origin main
```

Create and push a version tag:

```powershell
git tag v0.3.0
git push origin v0.3.0
```

## 8. GitHub Actions Release Flow

This repo should now have:

- `CI` workflow for lint, type-check, tests, build, and `twine check`
- `release.yml` workflow for tagged wheel/sdist publishing

Recommended secrets:

- `PYPI_API_TOKEN`

## 9. Post-Release Verification

On another machine:

```powershell
python -m pip uninstall -y lunadem
python -m pip install --no-cache-dir lunadem==0.3.0
python -c "import lunadem; print(lunadem.__version__)"
lunadem --help
lunadem download --test --output downloads
```

## 10. Troubleshooting

- If `lunardem` still appears in old code examples, update docs/examples before tagging.
- If native build fails on a machine without a compiler, install from the wheel built on CI or rely on the Python fallback path.
- If metadata model files need refresh, rerun `tools/train_metadata_cnns.py` and commit the regenerated `lunadem/assets/models/*` artifacts.
