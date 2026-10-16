$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '../..')
. (Join-Path $PSScriptRoot '../common.ps1')
if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) { throw 'Install Node.js 22+ LTS with npm.' }
node -e 'process.exit(parseInt(process.versions.node) >= 22 ? 0 : 1)'
Assert-Exit 'Node.js version check'
if (-not (Test-Path '.env')) {
    $tokenBytes = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $rng.GetBytes($tokenBytes)
    $rng.Dispose()
    $token = [Convert]::ToBase64String($tokenBytes)
    Set-Content '.env' "SPATIAL_TOKEN=$token" -Encoding ascii
}
if (-not (Test-Path 'apps/api/.venv/Scripts/python.exe')) {
    $pythonPath = Get-ProjectPython
    & $pythonPath -m venv apps/api/.venv
    Assert-Exit 'Python environment creation'
}
& apps/api/.venv/Scripts/python.exe -c 'import sys; sys.exit(0 if (3,12) <= sys.version_info[:2] < (3,14) else 1)'
Assert-Exit 'Virtual environment version check'
& apps/api/.venv/Scripts/python.exe -m pip install -r apps/api/requirements.lock.txt
Assert-Exit 'API dependency installation'
& apps/api/.venv/Scripts/python.exe scripts/verify/export_contract.py
Assert-Exit 'Contract export'
npm.cmd ci
Assert-Exit 'Web dependency installation'
Write-Output 'Ready. Run scripts/dev/start.ps1. Read SPATIAL_TOKEN from .env for the local console.'
