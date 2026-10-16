param([Parameter(Mandatory)][string]$Source, [Parameter(Mandatory)][string]$Destination)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$sourcePath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Source)
$destinationPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Destination)
if (-not $destinationPath.StartsWith($root + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Destination must stay inside this workspace.' }
Push-Location (Join-Path $root 'apps/api')
try {
    & "$root/apps/api/.venv/Scripts/python.exe" -m app.maintenance backup $sourcePath $destinationPath
    if ($LASTEXITCODE -ne 0) { throw "Backup failed (exit $LASTEXITCODE)." }
} finally { Pop-Location }
