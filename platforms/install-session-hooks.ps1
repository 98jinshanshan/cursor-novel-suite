# Install user-level Cursor hooks for workspace-local session archive.
param(
    [string]$SourceRoot = ""
)

$ErrorActionPreference = "Stop"
if (-not $SourceRoot) {
    $SourceRoot = Split-Path -Parent $PSScriptRoot
}

$destHooks = Join-Path $env:USERPROFILE ".cursor\hooks"
$destJson = Join-Path $env:USERPROFILE ".cursor\hooks.json"

New-Item -ItemType Directory -Force -Path $destHooks | Out-Null

Copy-Item -Force (Join-Path $SourceRoot "platforms\session-archive.py") (Join-Path $destHooks "session-archive.py")
Copy-Item -Force (Join-Path $SourceRoot "platforms\hooks\pre-compact-archive.ps1") (Join-Path $destHooks "pre-compact-archive.ps1")
Copy-Item -Force (Join-Path $SourceRoot "platforms\hooks\hooks.json") $destJson

Write-Host "OK: installed user hooks"
Write-Host "  hooks.json -> $destJson"
Write-Host "  scripts    -> $destHooks"
Write-Host "Reload Cursor window to activate preCompact / sessionEnd hooks."
