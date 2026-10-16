param([Parameter(Mandatory)][string]$Snapshot, [Parameter(Mandatory)][string]$Destination)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$snapshotPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Snapshot)
$destinationPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Destination)
if (-not $destinationPath.StartsWith($root + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Destination must stay inside this workspace.' }
if (Test-Path -LiteralPath $destinationPath) { throw 'Restore destination must be a new file; active databases are never replaced.' }
Push-Location (Join-Path $root 'apps/api')
try {
    & "$root/apps/api/.venv/Scripts/python.exe" -m app.maintenance restore $snapshotPath $destinationPath
    if ($LASTEXITCODE -ne 0) { throw "Restore failed (exit $LASTEXITCODE)." }
} finally { Pop-Location }
