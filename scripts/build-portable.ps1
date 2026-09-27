param(
    [string]$Python = "python",
    [string]$Output = "dist"
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

& $Python scripts/run_pyinstaller.py --noconfirm --clean --windowed --onefile `
    --name "OSRMapMaker" --distpath $Output --workpath "build\pyinstaller" `
    --specpath "build\pyinstaller" app.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Portable Windows build: $Output\OSRMapMaker.exe"
