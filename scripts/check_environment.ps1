$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Input = Join-Path $Root 'workspace/input.txt'
$Output = Join-Path $Root 'workspace/output/output.txt'
$Worker = Join-Path $Root 'capabilities/text_transform/worker.ps1'
$RuntimeManifest = Join-Path $Root 'spec/v0.2/runtime/RUNTIME_MANIFEST.md'

if (-not (Test-Path -LiteralPath $Input)) { throw 'Missing workspace/input.txt' }
if (-not (Test-Path -LiteralPath $Worker)) { throw 'Missing deterministic worker' }
if (-not (Test-Path -LiteralPath $RuntimeManifest)) { throw 'Missing spec/v0.2/runtime/RUNTIME_MANIFEST.md' }

$inputHashBefore = (Get-FileHash -Algorithm SHA256 -LiteralPath $Input).Hash.ToLowerInvariant()
$resultJson = & $Worker -InputPath $Input -OutputPath $Output
$result = $resultJson | ConvertFrom-Json
$inputHashAfter = (Get-FileHash -Algorithm SHA256 -LiteralPath $Input).Hash.ToLowerInvariant()
$outputText = [System.IO.File]::ReadAllText($Output)

if ($inputHashBefore -ne $inputHashAfter) { throw 'Input preservation check failed.' }
if ($outputText.TrimEnd("`r","`n") -ne 'HELLO WORLD') { throw "Unexpected output: $outputText" }

Remove-Item -LiteralPath $Output -Force
Write-Host 'FPO Sandbox Starter environment check: PASS'
Write-Host "Runtime manifest: $RuntimeManifest"
Write-Host "Worker output SHA256 was $($result.output_sha256)"
