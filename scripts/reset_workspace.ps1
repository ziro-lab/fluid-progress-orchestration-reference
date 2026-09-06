$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Out = Join-Path $Root 'workspace/output/output.txt'
if (Test-Path -LiteralPath $Out) { Remove-Item -LiteralPath $Out -Force }
Get-ChildItem -LiteralPath (Join-Path $Root 'runs') -Directory -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Write-Host 'Workspace reset complete.'
