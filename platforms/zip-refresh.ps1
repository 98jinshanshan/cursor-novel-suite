# Refresh Novel Suite from GitHub main zip (no git required) — preserves user data dirs.
param(
    [string]$Branch = "main",
    [string]$Repo = "98jinshanshan/cursor-novel-suite",
    [string]$Dest = "",
    [switch]$SkipDownload
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_suite-common.ps1"

if ($Repo -notmatch '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$') {
    throw "Invalid -Repo (expected owner/name): $Repo"
}
if ($Branch -match '[\s\\/:"|<>]') {
    throw "Invalid -Branch: $Branch"
}

$DestRoot = if ($Dest) { (Resolve-Path $Dest).Path } else { Get-SuiteRoot -StartDir $PSScriptRoot }
$zipUrl = "https://github.com/$Repo/archive/refs/heads/$Branch.zip"
if (-not $zipUrl.StartsWith("https://github.com/")) {
    throw "Refusing non-GitHub zip URL: $zipUrl"
}
$tempZip = Join-Path $env:TEMP "cursor-novel-suite-$Branch.zip"
$tempExtract = Join-Path $env:TEMP ("cursor-novel-suite-extract-" + [guid]::NewGuid().ToString("n"))

Write-Host "== zip refresh =="
Write-Host "  URL:  $zipUrl"
Write-Host "  To:   $DestRoot"
Write-Host "  Preserve: $($script:SuitePreserveDirNames -join ', ')"

try {
    if (-not $SkipDownload) {
        Write-Host "Downloading..."
        Invoke-WebRequest -Uri $zipUrl -OutFile $tempZip -UseBasicParsing
    } elseif (-not (Test-Path $tempZip)) {
        throw "SkipDownload set but zip missing: $tempZip"
    }

    New-Item -ItemType Directory -Force -Path $tempExtract | Out-Null
    Expand-Archive -Path $tempZip -DestinationPath $tempExtract -Force
    $srcRoot = Get-ChildItem -Path $tempExtract -Directory | Select-Object -First 1
    if (-not $srcRoot) { throw "Empty zip extract: $tempExtract" }

    Write-Host "Extracted: $($srcRoot.FullName)"
    $roboArgs = @(
        $srcRoot.FullName, $DestRoot,
        "/E", "/COPY:DAT", "/R:2", "/W:2",
        "/XD", (Get-SuiteRobocopyExcludeDirs),
        "/NFL", "/NDL", "/NJH", "/NJS", "/NC", "/NS"
    )
    & robocopy @roboArgs
    $rc = $LASTEXITCODE
    if (-not (Test-RobocopyOk -ExitCode $rc)) {
        throw "robocopy failed with exit code $rc"
    }
    Write-Host "OK: zip refresh complete (robocopy exit $rc)"
}
finally {
    if (Test-Path $tempExtract) { Remove-Item -Recurse -Force $tempExtract -ErrorAction SilentlyContinue }
}

Write-Host "Next: powershell -File platforms\patch-update.ps1 -SkipPull -Agents trae-cn"
