param([string]$Python = "python")

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
$env:PYTHONDONTWRITEBYTECODE = "1"
$reportDir = Join-Path $PSScriptRoot "..\artifacts\quality"
$reportPath = Join-Path $reportDir "pytest.xml"
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null

$sourceModules = @(
    "app.py",
    "commands.py",
    "constants.py",
    "models.py",
    "osr_map_maker.py",
    "project_services.py",
    "render_pillow.py",
    "render_tk.py",
    "renderers.py",
    "storage.py",
    "symbols.py",
    "validation.py",
    "geometry.py",
    "rendering.py",
    "scripts/export_vtt_reference.py",
    "scripts/regenerate_visual_references.py",
    "scripts/run_pyinstaller.py"
)

Write-Host "[1/4] Compile"
& $Python -m py_compile @sourceModules
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "[2/4] Tests (JUnit: $reportPath)"
& $Python -m pytest -q --junitxml=artifacts/quality/pytest.xml
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[3/4] Ruff"
& $Python -m ruff check .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[4/4] Mypy"
& $Python -m mypy --ignore-missing-imports @sourceModules
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
