param([string]$Python = "python")

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
& $Python -m pip install --upgrade ".[dev]"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python -m ruff --version
& $Python -m mypy --version
