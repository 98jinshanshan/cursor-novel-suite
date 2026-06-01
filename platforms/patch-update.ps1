# Patch-update an existing Novel Suite clone (git pull + skills + deps + doctor)
param(
    [string[]]$Agents = @("trae-cn"),
    [switch]$SkipPull,
    [switch]$SkipPip,
    [switch]$SkipTests
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
    throw "Cannot find Novel Suite root (need .novel-suite-root)."
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SuiteRoot = Get-SuiteRoot -StartDir $ScriptDir
Set-Location $SuiteRoot
Write-Host "Suite root: $SuiteRoot"

if (-not $SkipPull) {
    if (Test-Path (Join-Path $SuiteRoot ".git")) {
        Write-Host "== git pull =="
        git pull origin main
    } else {
        Write-Warning "No .git — skip pull. Re-download latest zip or clone if you need updates."
    }
}

Write-Host "== install skills =="
& (Join-Path $ScriptDir "install-skills.ps1") -Agents $Agents

if (-not $SkipPip) {
    Write-Host "== pip install =="
    pip install -r requirements-dev.txt
    pip install -r cursor-novel-writer/requirements.txt
    pip install -r cursor-novel-video/requirements.txt
}

Write-Host "== suite doctor =="
py -3 cursor-novel-writer/engine/novel_cli.py suite doctor --core-only
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
py -3 cursor-novel-writer/engine/novel_cli.py suite doctor
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "== Phase 0 skill check (novel-market-scan) =="
$phase0Skill = Join-Path $SuiteRoot ".trae\skills\novel-market-scan\SKILL.md"
$phase0Script = Join-Path $SuiteRoot ".trae\skills\novel-market-scan\scripts\intel_scan.py"
foreach ($agent in $Agents) {
    if ($agent -eq "trae-cn") {
        if (-not (Test-Path $phase0Skill)) { throw "Missing $phase0Skill — re-run install-skills.ps1" }
        if (-not (Test-Path $phase0Script)) { throw "Missing $phase0Script — need full monorepo + junction install" }
    }
}
Write-Host "OK: novel-market-scan (Phase 0) skill + intel_scan wrapper"

if (-not $SkipTests) {
    Write-Host "== pytest =="
    py -3 -m pytest cursor-novel-writer/tests cursor-novel-video/tests -m "not ffmpeg" -q
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Host ""
Write-Host "Patch update complete. SOLO smoke: Read novel-market-scan then run intel scan --period week"
Write-Host "SOLO sync (zip / mirror / git): powershell -File platforms/solo-sync.ps1 -UseZip -Agents trae-cn"
