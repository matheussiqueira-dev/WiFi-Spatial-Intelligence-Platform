param(
    [ValidateRange(1024, 65535)][int]$HttpPort = 4860,
    [ValidateRange(1024, 65535)][int]$WsPort = 4861,
    [switch]$Verification
)
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '../..')
. (Join-Path $PSScriptRoot '../common.ps1')
if ($HttpPort -eq $WsPort) { throw 'RuView REST and WebSocket ports must be different.' }
Assert-PortFree $HttpPort
Assert-PortFree $WsPort
$pythonPath = Join-Path (Get-Location) 'apps/api/.venv/Scripts/python.exe'
if (-not (Test-Path $pythonPath)) { throw 'Run bootstrap.ps1 first.' }
$project = if ($Verification) { 'wifi-spatial-f2-verification' } else { 'wifi-spatial-ruview' }
$credentialFile = if ($Verification) { 'artifacts/ruview-verification.env' } else { '.env.ruview' }
New-Item artifacts -ItemType Directory -Force | Out-Null
if (-not (Test-Path $credentialFile)) {
    $bytes = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $rng.GetBytes($bytes)
    $rng.Dispose()
    $credential = [Convert]::ToBase64String($bytes)
    Set-Content -LiteralPath $credentialFile -Value "SPATIAL_RUVIEW_TOKEN=$credential" -Encoding ascii
}
$oldHttpPort = $env:RUVIEW_HTTP_PORT
$oldWsPort = $env:RUVIEW_WS_PORT
try {
    $env:RUVIEW_HTTP_PORT = "$HttpPort"
    $env:RUVIEW_WS_PORT = "$WsPort"
    docker compose --env-file $credentialFile -f compose.ruview.yaml -p $project up --detach
    Assert-Exit 'Official RuView startup'
    & $pythonPath scripts/verify/ruview_probe.py --env-file $credentialFile --http-port $HttpPort --ws-port $WsPort
    Assert-Exit 'Official RuView REST and streaming readiness'
    Write-Output "RuView simulated ready: REST http://127.0.0.1:$HttpPort | WS ws://127.0.0.1:$WsPort/ws/sensing"
    if (-not $Verification -and ($HttpPort -ne 4860 -or $WsPort -ne 4861)) {
        Write-Output 'Set SPATIAL_RUVIEW_HTTP_URL and SPATIAL_RUVIEW_WS_URL in .env.ruview to the addresses above before starting the API.'
    }
} catch {
    # This launcher created only this named project; never remove other containers/volumes.
    docker compose --env-file $credentialFile -f compose.ruview.yaml -p $project down
    throw
} finally {
    $env:RUVIEW_HTTP_PORT = $oldHttpPort
    $env:RUVIEW_WS_PORT = $oldWsPort
}
