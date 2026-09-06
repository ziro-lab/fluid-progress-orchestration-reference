param(
    [Parameter(Mandatory=$true)][string]$InputPath,
    [Parameter(Mandatory=$true)][string]$OutputPath
)

$ErrorActionPreference = 'Stop'

$inFull  = [System.IO.Path]::GetFullPath($InputPath)
$outFull = [System.IO.Path]::GetFullPath($OutputPath)
if ($inFull -eq $outFull) {
    throw 'InputPath and OutputPath must be different.'
}
if (-not (Test-Path -LiteralPath $inFull -PathType Leaf)) {
    throw "Input file not found: $inFull"
}

$beforeHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $inFull).Hash.ToLowerInvariant()
$text = [System.IO.File]::ReadAllText($inFull)
$result = $text.ToUpperInvariant()
$outDir = [System.IO.Path]::GetDirectoryName($outFull)
[System.IO.Directory]::CreateDirectory($outDir) | Out-Null
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($outFull, $result, $utf8NoBom)
$afterHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $inFull).Hash.ToLowerInvariant()
if ($beforeHash -ne $afterHash) {
    throw 'Input file changed during worker execution.'
}

$outHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $outFull).Hash.ToLowerInvariant()
[ordered]@{
    status = 'completed'
    capability_id = 'local.text_uppercase'
    capability_revision = '1'
    input_path = $inFull
    input_sha256 = $afterHash
    output_path = $outFull
    output_sha256 = $outHash
} | ConvertTo-Json -Depth 4
