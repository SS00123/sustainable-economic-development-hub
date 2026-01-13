Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "Running pytest..."
pytest -q
