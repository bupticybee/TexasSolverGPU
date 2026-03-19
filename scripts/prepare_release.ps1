param(
    [string]$Version = "v0.1.0",
    [string]$SourceRepo = "",
    [switch]$SkipGitMetadata
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$releaseRepo = Split-Path -Parent $scriptRoot
if (-not $SourceRepo) {
    $SourceRepo = (Resolve-Path (Join-Path $releaseRepo "..\\gpu_solver")).Path
} else {
    $SourceRepo = (Resolve-Path $SourceRepo).Path
}

$winOutput = Join-Path $SourceRepo "win_output"
$viewerSource = Join-Path $SourceRepo "viewer\\viewer.py"
$quickStartSource = Join-Path $SourceRepo "quick_start"
$rangesSource = Join-Path $SourceRepo "ranges"

$requiredFiles = @(
    (Join-Path $winOutput "TexasSolverGpu.exe"),
    (Join-Path $winOutput "TexasSolverGpu_131.exe"),
    (Join-Path $winOutput "TexasSolverGpu_legacy_126.exe"),
    (Join-Path $winOutput "WebView2Loader.dll"),
    $viewerSource
)

foreach ($path in $requiredFiles) {
    if (-not (Test-Path $path)) {
        throw "Required file missing: $path"
    }
}

if (-not (Test-Path $quickStartSource)) {
    throw "Missing quick_start source: $quickStartSource"
}
if (-not (Test-Path $rangesSource)) {
    throw "Missing ranges source: $rangesSource"
}

$artifactRoot = Join-Path $releaseRepo ".artifacts"
$stagingRoot = Join-Path $artifactRoot "staging"
$bundleName = "TexasSolverGpu-$Version-windows-x64"
$bundleRoot = Join-Path $stagingRoot $bundleName
$zipPath = Join-Path $artifactRoot "$bundleName.zip"
$checksumsPath = Join-Path $releaseRepo "releases\\latest\\checksums.txt"
$manifestPath = Join-Path $releaseRepo "releases\\latest\\manifest.json"
$releaseNotesPath = Join-Path $releaseRepo "releases\\latest\\release_notes.md"

New-Item -ItemType Directory -Force -Path $artifactRoot, $stagingRoot | Out-Null
if (Test-Path $bundleRoot) {
    Remove-Item $bundleRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $bundleRoot | Out-Null

Copy-Item (Join-Path $winOutput "TexasSolverGpu.exe") $bundleRoot -Force
Copy-Item (Join-Path $winOutput "TexasSolverGpu_131.exe") $bundleRoot -Force
Copy-Item (Join-Path $winOutput "TexasSolverGpu_legacy_126.exe") $bundleRoot -Force
Copy-Item (Join-Path $winOutput "WebView2Loader.dll") $bundleRoot -Force

Copy-Item $quickStartSource (Join-Path $bundleRoot "quick_start") -Recurse -Force
Copy-Item $rangesSource (Join-Path $bundleRoot "ranges") -Recurse -Force

$bundleViewerDir = Join-Path $bundleRoot "viewer"
New-Item -ItemType Directory -Force -Path $bundleViewerDir | Out-Null
Copy-Item $viewerSource (Join-Path $bundleViewerDir "viewer.py") -Force
Copy-Item (Join-Path $releaseRepo "viewer\\README.md") (Join-Path $bundleViewerDir "README.md") -Force

if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}
Compress-Archive -Path (Join-Path $bundleRoot "*") -DestinationPath $zipPath -CompressionLevel Optimal

$zipHash = (Get-FileHash $zipPath -Algorithm "SHA256").Hash.ToLowerInvariant()
$exeHashes = @(
    (Get-FileHash (Join-Path $bundleRoot "TexasSolverGpu.exe") -Algorithm "SHA256"),
    (Get-FileHash (Join-Path $bundleRoot "TexasSolverGpu_131.exe") -Algorithm "SHA256"),
    (Get-FileHash (Join-Path $bundleRoot "TexasSolverGpu_legacy_126.exe") -Algorithm "SHA256"),
    (Get-FileHash (Join-Path $bundleRoot "WebView2Loader.dll") -Algorithm "SHA256")
)

$commit = ""
if (-not $SkipGitMetadata) {
    try {
        $commit = (git -C $SourceRepo rev-parse --short HEAD).Trim()
    } catch {
        $commit = ""
    }
}

$generatedAt = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")

@(
    "$zipHash *$bundleName.zip"
    ""
    ($exeHashes | ForEach-Object { "$($_.Hash.ToLowerInvariant()) *$($_.Path | Split-Path -Leaf)" })
) | Set-Content -Path $checksumsPath -Encoding ascii

$manifest = [ordered]@{
    version = $Version
    channel = "latest"
    platform = "windows-x64"
    bundle = "$bundleName.zip"
    sha256 = $zipHash
    generated_at = $generatedAt
    source_repo = "gpu_solver"
    source_commit = $commit
    required_runtime_files = @(
        "TexasSolverGpu.exe",
        "TexasSolverGpu_131.exe",
        "TexasSolverGpu_legacy_126.exe",
        "WebView2Loader.dll"
    )
    included_directories = @(
        "quick_start",
        "ranges",
        "viewer"
    )
} | ConvertTo-Json -Depth 5

$manifest | Set-Content -Path $manifestPath -Encoding utf8

$notes = @"
# $Version

## Files to upload to GitHub Release

- $bundleName.zip
- checksums.txt

## Compatibility notes

- Windows 10/11 x64
- NVIDIA GPU required
- WebView2 Runtime required
- Preferred launcher: TexasSolverGpu.exe
- Fallback runtimes: TexasSolverGpu_131.exe, TexasSolverGpu_legacy_126.exe

## Source traceability

- Source repo: gpu_solver
- Source commit: $commit
- Generated at: $generatedAt
"@

$notes | Set-Content -Path $releaseNotesPath -Encoding utf8

Write-Host "Prepared release bundle:"
Write-Host "  Repo:      $releaseRepo"
Write-Host "  Source:    $SourceRepo"
Write-Host "  Version:   $Version"
Write-Host "  Bundle:    $zipPath"
Write-Host "  SHA256:    $zipHash"
