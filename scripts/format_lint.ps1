Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "Running ruff format + check..."
ruff format .
ruff check .

Write-Host "Done."
