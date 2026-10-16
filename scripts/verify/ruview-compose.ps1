$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '../..')
. (Join-Path $PSScriptRoot '../common.ps1')
foreach ($port in @(4880, 4380, 4960, 4961)) { Assert-PortFree $port }
$pythonPath = Join-Path (Get-Location) 'apps/api/.venv/Scripts/python.exe'
if (-not (Test-Path $pythonPath)) { throw 'Run bootstrap.ps1 first.' }
New-Item artifacts -ItemType Directory -Force | Out-Null
if (-not (Test-Path artifacts/f2-compose.env)) {
    & $pythonPath -c 'from pathlib import Path; import secrets; Path("artifacts/f2-compose.env").write_text("SPATIAL_TOKEN=" + secrets.token_hex(32) + "\nSPATIAL_RUVIEW_TOKEN=" + secrets.token_hex(32) + "\n")'
    Assert-Exit 'Isolated credentials creation'
}
$composeArguments = @('compose', '--env-file', 'artifacts/f2-compose.env', '-f', 'compose.yaml', '-f', 'compose.ruview.yaml', '-f', 'compose.ruview.verify.yaml', '-p', 'wifi-spatial-f2-compose-verification')
$previousLegacyFlag = $env:SPATIAL_LEGACY_LAB_ENABLED
try {
    $env:SPATIAL_LEGACY_LAB_ENABLED = 'true'
    docker @composeArguments up --build --detach --wait
    Assert-Exit 'Isolated F2 stack startup'
    & $pythonPath scripts/verify/ruview_probe.py --env-file artifacts/f2-compose.env --http-port 4960 --ws-port 4961
    Assert-Exit 'Official RuView stream readiness'
    & $pythonPath scripts/verify/ruview_compose_smoke.py
    Assert-Exit 'Official stream and SQLite restart verification'
} finally {
    docker @composeArguments down
    Assert-Exit 'Isolated F2 stack shutdown (volume preserved)'
    $env:SPATIAL_LEGACY_LAB_ENABLED = $previousLegacyFlag
}
