# Install session-retrospect + session-lifecycle-reorder into IDE skill dirs.
param(
    [string[]]$Agents = @("cursor"),
    [switch]$AlsoAgents
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_suite-common.ps1"

$SuiteRoot = Get-SuiteRoot -StartDir (Split-Path -Parent $MyInvocation.MyCommand.Path)
$SessionSkills = Join-Path $SuiteRoot "skills"

function Remove-SkillDest {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return }
    Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction SilentlyContinue
}

function Install-OneSkill {
    param([string]$Source, [string]$Dest)
    Remove-SkillDest -Path $Dest
    $parent = Split-Path $Dest -Parent
    if (-not (Test-Path $parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    try {
        New-Item -ItemType Junction -Path $Dest -Target $Source | Out-Null
        $mode = "junction"
    } catch {
        Copy-Item -LiteralPath $Source -Destination $Dest -Recurse -Force
        $mode = "copy"
    }
    Write-Host "Installed $(Split-Path $Source -Leaf) -> $Dest ($mode)"
}

$targets = @()
if ($Agents -contains "cursor") {
    $targets += Join-Path $SuiteRoot ".cursor\skills"
    if ($AlsoAgents) { $targets += Join-Path $SuiteRoot ".agents\skills" }
}
if ($Agents -contains "qoder") {
    $targets += Join-Path $SuiteRoot ".qoder\skills"
}
if ($Agents -contains "trae-cn") {
    $targets += Join-Path $SuiteRoot ".trae\skills"
}

foreach ($name in @("session-retrospect", "session-lifecycle-reorder")) {
    $src = Join-Path $SessionSkills $name
    if (-not (Test-Path $src)) {
        Write-Host "SKIP: missing $src"
        continue
    }
    foreach ($root in $targets) {
        Install-OneSkill -Source $src -Dest (Join-Path $root $name)
    }
}

Write-Host "Done. Reload Cursor window (Ctrl+Shift+P -> Developer: Reload Window)."
