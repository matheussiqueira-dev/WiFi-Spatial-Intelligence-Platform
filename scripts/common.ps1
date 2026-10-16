$ErrorActionPreference = 'Stop'

function Assert-Exit([string]$Step) {
    if ($LASTEXITCODE -ne 0) { throw "$Step failed (exit $LASTEXITCODE)" }
}

function Assert-PortFree([int]$Port) {
    $listeners = [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners()
    if ($listeners | Where-Object { $_.Port -eq $Port }) {
        throw "Port $Port is already in use. Choose another port; no process was stopped."
    }
}

function Get-ProjectPython {
    $candidates = @('python', 'python3', "$env:LOCALAPPDATA/Programs/Python/Python312/python.exe", "$env:LOCALAPPDATA/Programs/Python/Python313/python.exe")
    foreach ($candidate in $candidates) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($command) {
            & $command.Source -c 'import sys; sys.exit(0 if (3,12) <= sys.version_info[:2] < (3,14) else 1)' 2>$null
            if ($LASTEXITCODE -eq 0) { return $command.Source }
        }
    }
    throw 'Install Python 3.12 or 3.13. No compatible Python executable was found.'
}
