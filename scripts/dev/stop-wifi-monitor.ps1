$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Set-Location -LiteralPath $projectRoot
if (-not (Test-Path runtime/wifi-monitor.lock)) { Write-Output 'No active collector lock.'; return }
$identity = Get-Content runtime/wifi-monitor.lock -Raw | ConvertFrom-Json
$process = Get-CimInstance Win32_Process -Filter "ProcessId=$([int]$identity.pid)"
if (-not $process -or $process.CommandLine -notlike '*scripts/network/collect_wifi.py*') {
    throw 'Collector ownership could not be verified. No process was stopped; inspect the lock manually.'
}
Set-Content runtime/wifi-monitor.stop -Value 'stop' -Encoding ascii
for ($attempt=0; $attempt -lt 40; $attempt++) {
    if (-not (Test-Path runtime/wifi-monitor.lock)) { Write-Output 'Host collector stopped cooperatively.'; return }
    Start-Sleep -Milliseconds 500
}
throw 'Collector is still shutting down. No process was killed.'
