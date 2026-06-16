# Install Novel Suite skills (writer + video) — path-agnostic
param(
    [string[]]$Agents = @("cursor", "qoder", "trae-cn"),
    [switch]$Global,
    [switch]$Copy,
    [switch]$AlsoAgents,
    [string]$CursorDest = ".cursor/skills"
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_suite-common.ps1"

$Agents = $Agents | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ }

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SuiteRoot = Get-SuiteRoot -StartDir $ScriptDir
$WriterSkills = Join-Path $SuiteRoot "cursor-novel-writer\skills"
$VideoSkills = Join-Path $SuiteRoot "cursor-novel-video\skills"

function Remove-SkillDest {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return }
    try {
        Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction Stop
        return
    } catch {
        Write-Host "WARN: Remove-Item failed for $Path — trying robocopy purge"
    }
    $empty = Join-Path $env:TEMP ("novel-suite-empty-" + [guid]::NewGuid().ToString("n"))
    New-Item -ItemType Directory -Force -Path $empty | Out-Null
    try {
        & robocopy $empty $Path /MIR /R:1 /W:1 /NFL /NDL /NJH /NJS /NC /NS | Out-Null
        if (Test-Path $Path) {
            Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction SilentlyContinue
        }
    } finally {
        Remove-Item -LiteralPath $empty -Recurse -Force -ErrorAction SilentlyContinue
    }
    if (Test-Path $Path) {
        throw "Cannot remove existing skill dest: $Path"
    }
}

function Copy-SkillTreeRobocopy {
    param([string]$Source, [string]$Dest)
    $parent = Split-Path -Parent $Dest
    if ($parent -and -not (Test-Path $parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    & robocopy $Source $Dest /E /COPY:DAT /R:1 /W:1 /NFL /NDL /NJH /NJS /NC /NS
    if (-not (Test-RobocopyOk -ExitCode $LASTEXITCODE)) {
        throw "robocopy failed for $Source -> $Dest (exit $LASTEXITCODE)"
    }
}

function Copy-SkillTreeWithFallback {
    param([string]$Source, [string]$Dest)
    try {
        Copy-Item -LiteralPath $Source -Destination $Dest -Recurse -Force -ErrorAction Stop
        return "copy"
    } catch {
        Write-Host "WARN: Copy-Item failed for $(Split-Path $Source -Leaf) — $($_.Exception.Message)"
        Write-Host "WARN: falling back to robocopy"
        Copy-SkillTreeRobocopy -Source $Source -Dest $Dest
        return "robocopy"
    }
}

function Install-SkillDir {
    param(
        [string]$SourceDir,
        [string]$DestRoot,
        [string]$Label
    )
    if (-not (Test-Path $SourceDir)) {
        Write-Host "SKIP: missing $SourceDir"
        return
    }
    New-Item -ItemType Directory -Force -Path $DestRoot | Out-Null
    Get-ChildItem $SourceDir -Directory | ForEach-Object {
        $dest = Join-Path $DestRoot $_.Name
        Remove-SkillDest -Path $dest
        $mode = "copy"
        if (-not $Copy) {
            try {
                New-Item -ItemType Junction -Path $dest -Target $_.FullName | Out-Null
                $mode = "junction"
            } catch {
                Write-Host "WARN: junction failed for $($_.Name); using copy/robocopy"
                $mode = Copy-SkillTreeWithFallback -Source $_.FullName -Dest $dest
            }
        } else {
            $mode = Copy-SkillTreeWithFallback -Source $_.FullName -Dest $dest
        }
        Write-Host "Installed $($_.Name) -> $dest ($Label, $mode)"
    }
}

$cursorRoots = @()
if ($Global) {
    $cursorRoots += "$env:USERPROFILE\.cursor\skills"
} else {
    $cursorRoots += Join-Path $SuiteRoot $CursorDest
    if ($AlsoAgents) {
        $cursorRoots += Join-Path $SuiteRoot ".agents\skills"
    }
}

$AgentPathMap = @{
    "cursor"  = $cursorRoots
    "qoder"   = @($(if ($Global) { "$env:USERPROFILE\.qoder\skills" } else { Join-Path $SuiteRoot ".qoder\skills" }))
    "trae-cn" = @($(if ($Global) { "$env:USERPROFILE\.trae-cn\skills" } else { Join-Path $SuiteRoot ".trae\skills" }))
}

Write-Host "Suite root: $SuiteRoot"

foreach ($agent in $Agents) {
    if (-not $AgentPathMap.ContainsKey($agent)) { continue }
    foreach ($destRoot in $AgentPathMap[$agent]) {
        if ([string]::IsNullOrWhiteSpace($destRoot)) { continue }
        Install-SkillDir -SourceDir $WriterSkills -DestRoot $destRoot -Label $agent
        Install-SkillDir -SourceDir $VideoSkills -DestRoot $destRoot -Label "$agent-video"
    }
}

Write-Host "Done. Run: py -3 cursor-novel-writer/engine/novel_cli.py suite doctor"
Write-Host ""
Write-Host "Rules Packs: powershell -File platforms/install-rules-packs.ps1 -Agents cursor,codex,trae-cn,qoder,openclaw,generic-agent -DryRun"
Write-Host ""
Write-Host "Phase 0 = novel-market-scan (NOT a phase-0/ folder). Verify:"
Write-Host "  .trae/skills/novel-market-scan/scripts/intel_scan.py  (trae-cn)"
Write-Host "  See docs/standards/SKILLS-INSTALL.md"
