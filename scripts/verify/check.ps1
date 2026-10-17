param([switch]$SkipE2E, [switch]$RuView, [int]$RuViewHttpPort = 4860, [int]$RuViewWsPort = 4861, [string]$Browsers = 'chromium,webkit')
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '../..')
. (Join-Path $PSScriptRoot '../common.ps1')
if ($RuView -and $SkipE2E) { throw '-RuView requires the browser integration checks.' }
$pythonPath = Join-Path (Get-Location) 'apps/api/.venv/Scripts/python.exe'
& $pythonPath -m ruff check apps/api scripts/verify scripts/network
Assert-Exit 'Python lint'
& $pythonPath -m ruff format --check apps/api scripts/verify scripts/network
Assert-Exit 'Python format'
& $pythonPath -m mypy --config-file apps/api/pyproject.toml apps/api/app
Assert-Exit 'Python types'
& $pythonPath scripts/verify/export_contract.py --check
Assert-Exit 'Published contracts'
& $pythonPath -m pytest apps/api/tests -q
Assert-Exit 'Backend tests'
& $pythonPath -m pytest scripts/verify/tests -q
Assert-Exit 'Launcher integration tests'
npm.cmd run lint
Assert-Exit 'Frontend lint'
npm.cmd run format:check
Assert-Exit 'Frontend formatting'
npm.cmd run typecheck
Assert-Exit 'TypeScript'
npm.cmd run test:web
Assert-Exit 'Frontend contract tests'
if ($SkipE2E) { npm.cmd run build } else { npm.cmd run build:e2e }
Assert-Exit 'Production build'
if (-not $SkipE2E) {
    Assert-PortFree 4810
    Assert-PortFree 4310
    $previousRuViewFlag = $env:E2E_RUVIEW
    $previousRuViewToken = $env:SPATIAL_RUVIEW_TOKEN
    $previousRuViewHttp = $env:E2E_RUVIEW_HTTP_URL
    $previousRuViewWs = $env:E2E_RUVIEW_WS_URL
    $previousBrowsers = $env:E2E_BROWSERS
    $previousProfile = $env:E2E_PROFILE
    $ruviewStarted = $false
    try {
        if ($RuView) {
            & scripts/dev/start-ruview.ps1 -Verification -HttpPort $RuViewHttpPort -WsPort $RuViewWsPort
            $ruviewStarted = $true
            $tokenLine = Get-Content artifacts/ruview-verification.env | Where-Object { $_ -match '^SPATIAL_RUVIEW_TOKEN=' }
            $env:SPATIAL_RUVIEW_TOKEN = ($tokenLine -split '=', 2)[1]
            $env:E2E_RUVIEW = '1'
            $env:E2E_RUVIEW_HTTP_URL = "http://127.0.0.1:$RuViewHttpPort"
            $env:E2E_RUVIEW_WS_URL = "ws://127.0.0.1:$RuViewWsPort/ws/sensing"
        } else { $env:E2E_RUVIEW = '0' }
        $env:E2E_BROWSERS = $Browsers
        $env:E2E_PROFILE = 'lab'
        npm.cmd run test:e2e
        Assert-Exit 'End-to-end tests'
        # Same build, API restarted with the commercial-br capability profile.
        $env:E2E_BROWSERS = 'chromium'
        $env:E2E_PROFILE = 'commercial-br'
        npm.cmd run test:e2e
        Assert-Exit 'End-to-end tests (commercial-br profile)'
    } finally {
        # Restore first so a failing shutdown neither leaks the credential nor masks errors.
        $env:E2E_RUVIEW = $previousRuViewFlag
        $env:SPATIAL_RUVIEW_TOKEN = $previousRuViewToken
        $env:E2E_RUVIEW_HTTP_URL = $previousRuViewHttp
        $env:E2E_RUVIEW_WS_URL = $previousRuViewWs
        $env:E2E_BROWSERS = $previousBrowsers
        $env:E2E_PROFILE = $previousProfile
        if ($ruviewStarted) {
            docker compose --env-file artifacts/ruview-verification.env -f compose.ruview.yaml -p wifi-spatial-f2-verification down
            if ($LASTEXITCODE -ne 0) { Write-Warning "Verification RuView shutdown failed (exit $LASTEXITCODE)." }
        }
    }
}
