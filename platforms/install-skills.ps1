# Install Novel Suite skills (writer + video) — path-agnostic
param(
    [string[]]$Agents = @("cursor", "qoder", "trae-cn"),
    [switch]$Global,
    [switch]$Copy
)

$ErrorActionPreference = "Stop"

$Agents = $Agents | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ }

function Get-SuiteRoot {
    param([string]$StartDir)
    $current = (Resolve-Path $StartDir).Path
    for ($i = 0; $i -lt 12; $i++) {
        if (Test-Path (Join-Path $current ".novel-suite-root")) {
            $writerCli = Join-Path $current "cursor-novel-writer\engine\novel_cli.py"
            if (Test-Path $writerCli) { return $current }
        }
        $parent = Split-Path -Parent $current
        if ($parent -eq $current) { break }
        $current = $parent
    }
    throw "Cannot find Novel Suite root (need .novel-suite-root). Open monorepo root or set NOVEL_SUITE_ROOT."
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SuiteRoot = Get-SuiteRoot -StartDir $ScriptDir
$WriterSkills = Join-Path $SuiteRoot "cursor-novel-writer\skills"
$VideoSkills = Join-Path $SuiteRoot "cursor-novel-video\skills"

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
        if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
        $mode = "copy"
        if (-not $Copy) {
            try {
                New-Item -ItemType Junction -Path $dest -Target $_.FullName | Out-Null
                $mode = "junction"
            } catch {
                Write-Host "WARN: junction failed for $($_.Name); using copy"
                Copy-Item -Recurse $_.FullName $dest
            }
        } else {
            Copy-Item -Recurse $_.FullName $dest
        }
        if ($mode -eq "junction") {
            Write-Host "Linked $($_.Name) -> $dest ($Label, junction)"
        } else {
            Write-Host "Installed $($_.Name) -> $dest ($Label, copy)"
        }
    }
}

$AgentPathMap = @{
    "cursor"   = @(
        $(if ($Global) { "$env:USERPROFILE\.cursor\skills" } else { Join-Path $SuiteRoot ".agents\skills" }),
        $(if (-not $Global) { Join-Path $SuiteRoot ".cursor\skills" })
    )
    "qoder"    = @($(if ($Global) { "$env:USERPROFILE\.qoder\skills" } else { Join-Path $SuiteRoot ".qoder\skills" }))
    "trae-cn"  = @($(if ($Global) { "$env:USERPROFILE\.trae-cn\skills" } else { Join-Path $SuiteRoot ".trae\skills" }))
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
