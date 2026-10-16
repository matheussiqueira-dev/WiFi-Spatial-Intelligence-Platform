param([switch]$Background, [switch]$GatewayProbes, [switch]$ChannelSurvey, [ValidateRange(1024,65535)][int]$ApiPort=8000)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Set-Location -LiteralPath $projectRoot
$pythonPath = Join-Path $projectRoot 'apps/api/.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Run bootstrap.ps1 first.' }
if (Test-Path runtime/wifi-monitor.lock) { throw 'Collector lock exists. Check its PID or use stop-wifi-monitor.ps1 before starting another.' }
New-Item artifacts -ItemType Directory -Force | Out-Null
$collectorArgs = @('scripts/network/collect_wifi.py','--api-url',"http://127.0.0.1:$ApiPort")
if ($GatewayProbes) { $collectorArgs += '--gateway-probes' }
if ($ChannelSurvey) { $collectorArgs += '--channel-survey' }
if ($Background) {
    $process = Start-Process -FilePath $pythonPath -ArgumentList $collectorArgs -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput artifacts/wifi-monitor.stdout.log -RedirectStandardError artifacts/wifi-monitor.stderr.log -PassThru
    $deadline = (Get-Date).AddSeconds(10)
    while (-not (Test-Path runtime/wifi-monitor.lock)) {
        if ($process.HasExited -or (Get-Date) -gt $deadline) { throw 'Collector did not acquire its lock; inspect artifacts/wifi-monitor.stderr.log.' }
        Start-Sleep -Milliseconds 250
        $process.Refresh()
    }
    Write-Output "Host Wi-Fi collector started (PID $($process.Id)). No Windows service installed."
} else {
    & $pythonPath @collectorArgs
    if ($LASTEXITCODE -ne 0) { throw 'Host Wi-Fi collector stopped with an error.' }
}
