$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
$env:PYTHONDONTWRITEBYTECODE = "1"

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
    "symbols.py"
)

python -m py_compile @sourceModules
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m pytest -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$ruff = Get-Command ruff -ErrorAction SilentlyContinue
if ($ruff) {
    ruff check .
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$mypy = Get-Command mypy -ErrorAction SilentlyContinue
if ($mypy) {
    mypy --ignore-missing-imports @sourceModules
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
