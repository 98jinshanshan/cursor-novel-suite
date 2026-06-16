# Install Novel Suite Rules Packs (thin IDE adapters) — path-agnostic
param(
    [string[]]$Agents = @("cursor", "codex", "trae-cn", "qoder", "openclaw", "generic-agent"),
    [string]$DestRoot = ".agent-rules",
    [switch]$Copy,
    [switch]$UseIdeDirs,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_suite-common.ps1"

$Agents = $Agents | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ }

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SuiteRoot = Get-SuiteRoot -StartDir $ScriptDir
$SourceRoot = Join-Path $SuiteRoot "novel-suite\rules-packs"

$ValidAgents = @("cursor", "codex", "trae-cn", "qoder", "openclaw", "generic-agent")
$EntryMap = @{
    "cursor"         = "rules.md"
    "codex"          = "AGENTS.md"
    "trae-cn"        = "rules.md"
    "qoder"          = "rules.md"
    "openclaw"       = "rules.md"
    "generic-agent"  = "rules.md"
}

function Get-AgentDest {
    param([string]$Agent, [string]$Root)
    if ($UseIdeDirs) {
        switch ($Agent) {
            "cursor"        { return Join-Path $SuiteRoot ".cursor\rules\novel-suite" }
            "codex"         { return Join-Path $SuiteRoot ".codex\novel-suite" }
            "trae-cn"       { return Join-Path $SuiteRoot ".trae\rules\novel-suite" }
            "qoder"         { return Join-Path $SuiteRoot ".qoder\rules\novel-suite" }
            "openclaw"      { return Join-Path $SuiteRoot ".openclaw\rules\novel-suite" }
            "generic-agent" { return Join-Path $Root "generic-agent" }
        }
    }
    return Join-Path $Root $Agent
}

if (-not (Test-Path $SourceRoot)) {
    throw "Rules pack source not found: $SourceRoot"
}

$DestBase = if ([System.IO.Path]::IsPathRooted($DestRoot)) { $DestRoot } else { Join-Path $SuiteRoot $DestRoot }

Write-Host "Suite root: $SuiteRoot"
Write-Host "Rules source: $SourceRoot"
Write-Host "Dest base: $DestBase"
if ($DryRun) { Write-Host "DRY RUN — no files will be written" }

$planned = @()
foreach ($agent in $Agents) {
    if ($agent -notin $ValidAgents) {
        Write-Host "WARN: unknown agent '$agent' — skipped"
        continue
    }
    $src = Join-Path $SourceRoot $agent
    if (-not (Test-Path $src)) {
        throw "Missing rules pack source: $src"
    }
    $dest = Get-AgentDest -Agent $agent -Root $DestBase
    $planned += [PSCustomObject]@{ Agent = $agent; Source = $src; Dest = $dest }
}

foreach ($item in $planned) {
    Write-Host "  $($item.Agent) -> $($item.Dest)"
    if ($DryRun) { continue }
    if (-not (Test-Path $item.Dest)) {
        New-Item -ItemType Directory -Force -Path $item.Dest | Out-Null
    }
    if ($Copy) {
        & robocopy $item.Source $item.Dest /E /COPY:DAT /R:1 /W:1 /NFL /NDL /NJH /NJS /NC /NS | Out-Null
        if (-not (Test-RobocopyOk $LASTEXITCODE)) {
            throw "robocopy failed for $($item.Agent)"
        }
    } else {
        Get-ChildItem -LiteralPath $item.Source -File | ForEach-Object {
            Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $item.Dest $_.Name) -Force
        }
        if (Test-Path (Join-Path $item.Source "README.md")) {
            Copy-Item -LiteralPath (Join-Path $item.Source "README.md") -Destination (Join-Path $item.Dest "README.md") -Force
        }
    }
}

if (-not $DryRun) {
    Write-Host "Done. Rules packs installed under $DestBase"
} else {
    Write-Host "DryRun complete. $($planned.Count) agent(s) validated."
}
