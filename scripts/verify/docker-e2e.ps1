param([switch]$SkipBrowser)
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '../..')
. (Join-Path $PSScriptRoot '../common.ps1')
Assert-PortFree 4900
Assert-PortFree 4400
New-Item artifacts -ItemType Directory -Force | Out-Null
$credentialFile = 'artifacts/native-e2e.env'
if (-not (Test-Path $credentialFile)) {
    $bytes = New-Object byte[] 32
    $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    $rng.GetBytes($bytes)
    $rng.Dispose()
    Set-Content -LiteralPath $credentialFile -Value ('SPATIAL_TOKEN=' + [Convert]::ToBase64String($bytes)) -Encoding ascii
}
$names = @('E2E_EXTERNAL','E2E_COMPOSE_PROJECT','E2E_TOKEN','E2E_API_PORT','E2E_WEB_PORT','E2E_RUVIEW','SPATIAL_LEGACY_LAB_ENABLED')
$previous = @{}
foreach ($name in $names) { $previous[$name] = [Environment]::GetEnvironmentVariable($name, 'Process') }
$composeArgs = @('compose','--env-file',$credentialFile,'-f','compose.yaml','-f','compose.native.verify.yaml','-p','wifi-spatial-native-e2e')
try {
    $env:SPATIAL_LEGACY_LAB_ENABLED = 'false'
    docker @composeArgs up --build --detach --wait
    Assert-Exit 'Independent stack startup'
    $env:E2E_EXTERNAL = '1'
    $env:E2E_COMPOSE_PROJECT = 'wifi-spatial-native-e2e'
    $env:E2E_TOKEN = ((Get-Content $credentialFile | Where-Object { $_ -match '^SPATIAL_TOKEN=' }) -split '=',2)[1]
    $env:E2E_API_PORT = '4900'
    $env:E2E_WEB_PORT = '4400'
    $env:E2E_RUVIEW = '0'
    if (-not $SkipBrowser) {
        npm.cmd run test:e2e
        Assert-Exit 'Independent Docker end-to-end tests'
    }
    & apps/api/.venv/Scripts/python.exe scripts/verify/native_compose_smoke.py
    Assert-Exit 'Independent restart and analytics persistence'
} finally {
    docker @composeArgs down
    foreach ($name in $names) { [Environment]::SetEnvironmentVariable($name, $previous[$name], 'Process') }
}
