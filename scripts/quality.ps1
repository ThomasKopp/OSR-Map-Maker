$ErrorActionPreference = "Stop"
$env:PYTHONDONTWRITEBYTECODE = "1"

python -m py_compile osr_map_maker.py models.py constants.py renderers.py project_services.py
python -m pytest -q

$ruff = Get-Command ruff -ErrorAction SilentlyContinue
if ($ruff) {
    ruff check .
}

$mypy = Get-Command mypy -ErrorAction SilentlyContinue
if ($mypy) {
    mypy --ignore-missing-imports osr_map_maker.py models.py constants.py renderers.py project_services.py
}
