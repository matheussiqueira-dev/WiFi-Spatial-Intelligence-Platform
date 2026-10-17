param(
    [ValidateRange(1024, 65535)][int]$ApiPort = 8000,
    [ValidateRange(1024, 65535)][int]$WebPort = 3000
)
$ErrorActionPreference = 'Stop'
$projectRoot = Resolve-Path (Join-Path $PSScriptRoot '../..')
Set-Location $projectRoot
if (-not (Test-Path '.env')) { throw 'Run scripts/setup/bootstrap.ps1 first' }
. (Join-Path $PSScriptRoot '../common.ps1')
if ($ApiPort -eq $WebPort) { throw 'API and web ports must be different.' }
Assert-PortFree $ApiPort
Assert-PortFree $WebPort
if (-not (Test-Path 'apps/api/.venv/Scripts/python.exe')) { throw 'Run bootstrap.ps1 first' }
New-Item artifacts -ItemType Directory -Force | Out-Null
$previousOrigins = $env:SPATIAL_ORIGINS
$previousApiUrl = $env:NEXT_PUBLIC_API_URL
$env:SPATIAL_ORIGINS = "[`"http://127.0.0.1:$WebPort`",`"http://localhost:$WebPort`"]"
$env:NEXT_PUBLIC_API_URL = "http://127.0.0.1:$ApiPort"
$apiProcess = $null
try {
    $apiProcess = Start-Process -FilePath "$projectRoot/apps/api/.venv/Scripts/python.exe" -ArgumentList @('-m','uvicorn','app.main:create_app','--factory','--app-dir','apps/api','--host','127.0.0.1','--port',"$ApiPort",'--ws-max-size','4096','--ws-max-queue','16','--no-proxy-headers') -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput "$projectRoot/artifacts/api.stdout.log" -RedirectStandardError "$projectRoot/artifacts/api.stderr.log" -PassThru
    $ready = $false
    for ($attempt = 0; $attempt -lt 40; $attempt++) {
        if ($apiProcess.HasExited) { throw 'API exited during startup. Inspect artifacts/api.stderr.log; confirm a valid SPATIAL_TOKEN in .env.' }
        try {
            $health = Invoke-RestMethod "http://127.0.0.1:$ApiPort/api/v1/health" -TimeoutSec 1
            if ($health.status -eq 'ok') { $ready = $true; break }
        } catch { Start-Sleep -Milliseconds 250 }
    }
    if (-not $ready) { throw 'API startup timed out. Inspect artifacts/api.stderr.log.' }
    Write-Output "API: http://127.0.0.1:$ApiPort/api/v1/health | Console: http://127.0.0.1:$WebPort/dashboard"
    npm.cmd run dev --workspace apps/web -- --port $WebPort
    Assert-Exit 'Web development server'
} finally {
    if ($apiProcess -and -not $apiProcess.HasExited) { Stop-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue }
    $env:SPATIAL_ORIGINS = $previousOrigins
    $env:NEXT_PUBLIC_API_URL = $previousApiUrl
}
