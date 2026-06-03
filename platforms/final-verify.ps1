# Novel Suite — unified local verification before declaring a code task done.
# Usage: powershell -File platforms/final-verify.ps1 [-ChangedOnly] [-SkipPytest] [-SkipMarkdown]

param(
    [switch]$ChangedOnly,
    [switch]$SkipPytest,
    [switch]$SkipMarkdown,
    [string]$BaseRef = "HEAD"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$failures = @()
$summary = [ordered]@{}

Write-Host "== Novel Suite Final Verification ==" -ForegroundColor Cyan
Write-Host "Repo: $RepoRoot"

Write-Host "`n-- Changed files (git) --"
$changedTracked = @(git diff --name-only --diff-filter=ACMRTUXB "$BaseRef" -- 2>$null)
$changedUntracked = @(git ls-files --others --exclude-standard 2>$null)
$changedAll = @($changedTracked + $changedUntracked | Sort-Object -Unique)
if ($changedAll.Count -eq 0) {
    Write-Host "(none vs $BaseRef)"
} else {
    $changedAll | ForEach-Object { Write-Host "  $_" }
}
$summary["changed_files"] = $changedAll.Count

if (-not $SkipPytest) {
    Write-Host "`n-- pytest (-m 'not ffmpeg') --"
    & py -3 -m pytest -m "not ffmpeg" -q
    if ($LASTEXITCODE -ne 0) {
        $failures += "pytest failed (exit $LASTEXITCODE)"
    } else {
        $summary["pytest"] = "passed"
    }
} else {
    $summary["pytest"] = "skipped"
}

Write-Host "`n-- pyright --"
$pyrightArgs = @("--yes", "pyright", "-p", "pyrightconfig.json")
if ($ChangedOnly) {
    $pyFiles = $changedAll | Where-Object { $_ -match '\.py$' }
    if ($pyFiles.Count -eq 0) {
        Write-Host "(ChangedOnly: no .py changes — skip pyright)"
        $summary["pyright"] = "skipped (no .py changes)"
    } else {
        $pyrightArgs += $pyFiles
        npx @pyrightArgs
        if ($LASTEXITCODE -ne 0) { $failures += "pyright failed" } else { $summary["pyright"] = "passed" }
    }
} else {
    npx @pyrightArgs
    if ($LASTEXITCODE -ne 0) { $failures += "pyright failed" } else { $summary["pyright"] = "passed" }
}

if (-not $SkipMarkdown) {
    Write-Host "`n-- markdownlint-cli2 (CI-aligned globs + intel/radar) --"
    if (Test-Path ".markdownlint-cli2.jsonc") {
        $mdGlobs = @(
            "cursor-novel-writer/**/*.md",
            "cursor-novel-video/**/*.md",
            "docs/**/*.md",
            "intel/**/*.md",
            "skills/**/*.md",
            ".cursor/rules/**/*.mdc",
            "novels/README.md",
            "*.md"
        )
        npx --yes markdownlint-cli2 @mdGlobs
        if ($LASTEXITCODE -ne 0) { $failures += "markdownlint failed" } else { $summary["markdownlint"] = "passed" }

        Write-Host "`n-- intel radar generator contract (pytest) --"
        & py -3 -m pytest tests/test_intel_radar_markdown.py -q
        if ($LASTEXITCODE -ne 0) {
            $failures += "intel radar markdown contract failed"
        } else {
            $summary["intel_radar_md"] = "passed"
        }
    } else {
        Write-Host "(no .markdownlint-cli2.jsonc — skip)"
        $summary["markdownlint"] = "skipped (no config)"
    }
} else {
    $summary["markdownlint"] = "skipped"
    $summary["intel_radar_md"] = "skipped"
}

Write-Host "`n== Final Verification Summary ==" -ForegroundColor Cyan
foreach ($kv in $summary.GetEnumerator()) {
    Write-Host ("  {0}: {1}" -f $kv.Key, $kv.Value)
}

if ($failures.Count -gt 0) {
    Write-Host "`nFAILED:" -ForegroundColor Red
    $failures | ForEach-Object { Write-Host "  - $_" }
    exit 1
}

Write-Host "`nOK: all checks passed." -ForegroundColor Green
exit 0
