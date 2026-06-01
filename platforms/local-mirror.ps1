# Mirror code from dev machine (e.g. G:\CURSOR) into SOLO test workspace — preserves user data dirs.
param(
    [Parameter(Mandatory = $true)]
    [string]$Source,
    [string]$Dest = "",
    [switch]$WhatIfOnly
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_suite-common.ps1"

$SourceRoot = (Resolve-Path $Source).Path
if (-not (Test-Path (Join-Path $SourceRoot ".novel-suite-root"))) {
    throw "Source is not a Novel Suite root (missing .novel-suite-root): $SourceRoot"
}

$DestRoot = if ($Dest) { (Resolve-Path $Dest).Path } else { Get-SuiteRoot -StartDir $PSScriptRoot }
if ($SourceRoot -eq $DestRoot) {
    Write-Host "SKIP: Source and destination are the same."
    exit 0
}

Write-Host "== local mirror =="
Write-Host "  From: $SourceRoot"
Write-Host "  To:   $DestRoot"
Write-Host "  Preserve: $($script:SuitePreserveDirNames -join ', ')"

$roboArgs = @(
    $SourceRoot, $DestRoot,
    "/E", "/COPY:DAT", "/R:2", "/W:2",
    "/XD", (Get-SuiteRobocopyExcludeDirs),
    "/NFL", "/NDL", "/NJH", "/NJS", "/NC", "/NS"
)
if ($WhatIfOnly) { $roboArgs += "/L" }

& robocopy @roboArgs
$rc = $LASTEXITCODE
if (-not (Test-RobocopyOk -ExitCode $rc)) {
    throw "robocopy failed with exit code $rc"
}

Write-Host "OK: local mirror complete (robocopy exit $rc)"
Write-Host "Next: powershell -File platforms\patch-update.ps1 -SkipPull -Agents trae-cn"
