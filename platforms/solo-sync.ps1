# SOLO / test client sync — local mirror > git pull > HTTP zip (default for non-git clients)
param(
    [string]$Source = "",
    [switch]$UseZip,
    [switch]$UseGit,
    [string[]]$Agents = @("trae-cn"),
    [switch]$SkipPip,
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_suite-common.ps1"

$SuiteRoot = Get-SuiteRoot -StartDir $PSScriptRoot
Set-Location $SuiteRoot
Write-Host "SOLO sync — suite root: $SuiteRoot"

$channel = "zip"
if ($UseGit) {
    $channel = "git"
} elseif ($UseZip) {
    $channel = "zip"
} elseif ($Source) {
    $channel = "mirror"
} elseif (Test-Path (Join-Path $SuiteRoot ".git")) {
    $channel = "git"
} else {
    $channel = "zip"
    Write-Host "No .git and no -Source — using HTTP zip (SOLO-safe default)."
}

switch ($channel) {
    "mirror" {
        Write-Host "== channel: local mirror =="
        & (Join-Path $PSScriptRoot "local-mirror.ps1") -Source $Source -Dest $SuiteRoot
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    "git" {
        Write-Host "== channel: git pull =="
        if (-not (Test-Path (Join-Path $SuiteRoot ".git"))) {
            throw "UseGit set but .git missing. Use -UseZip or git clone first."
        }
        git -C $SuiteRoot pull origin main
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    "zip" {
        Write-Host "== channel: HTTP zip =="
        & (Join-Path $PSScriptRoot "zip-refresh.ps1") -Dest $SuiteRoot
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
}

Write-Host "== post-sync: patch-update (skills, pip, doctor, pytest) =="
$patchParams = @{
    SkipPull = $true
    Agents   = $Agents
}
if ($SkipPip) { $patchParams.SkipPip = $true }
if ($SkipTests) { $patchParams.SkipTests = $true }
& (Join-Path $PSScriptRoot "patch-update.ps1") @patchParams
exit $LASTEXITCODE
