# Scan staged + untracked-to-commit paths for leaked API keys / forbidden fingerprints.
# Usage: powershell -File platforms/scan-staged-secrets.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $RepoRoot

$failures = @()

function Test-Sha256Forbidden {
    param([string]$Content, [string]$File)
    $fpPath = Join-Path $RepoRoot "platforms\secret-fingerprints.json"
    if (-not (Test-Path $fpPath)) { return }
    $fps = (Get-Content $fpPath -Raw | ConvertFrom-Json).forbidden_sha256
    foreach ($entry in $fps) {
        if ($Content -match 'sk-[A-Za-z0-9]{20,}') {
            $matches = [regex]::Matches($Content, 'sk-[A-Za-z0-9]{20,}')
            foreach ($m in $matches) {
                $sha = [BitConverter]::ToString(
                    [Security.Cryptography.SHA256]::Create().ComputeHash(
                        [Text.Encoding]::UTF8.GetBytes($m.Value)
                    )
                ).Replace("-", "").ToLowerInvariant()
                if ($sha -eq $entry.sha256) {
                    $failures += "FORBIDDEN fingerprint $($entry.id) in $File"
                }
            }
        }
    }
}

$skPattern = [regex]'sk-[A-Za-z0-9]{24,}'
$files = @()
$prev = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$staged = @(git diff --cached --name-only --diff-filter=ACMRT 2>$null)
$unstaged = @(git ls-files --others --exclude-standard 2>$null)
$ErrorActionPreference = $prev
$candidates = @($staged + $unstaged | Sort-Object -Unique)

foreach ($f in $candidates) {
    if (-not (Test-Path $f)) { continue }
    if ($f -match '(?i)(platforms/data/|local-secrets|credentials\.json|\.env$)') { continue }
    if ($f -match '\.(png|jpg|jpeg|gif|webp|mp4|safetensors|ckpt|zip|epub|pyc|woff2?)$') { continue }
    try {
        $content = Get-Content -Path $f -Raw -ErrorAction Stop
    } catch { continue }
    if ($skPattern.IsMatch($content)) {
        $failures += "Possible API key (sk-*) in $f"
    }
    Test-Sha256Forbidden -Content $content -File $f
}

if ($failures.Count -gt 0) {
    Write-Host "SECRET SCAN FAIL:" -ForegroundColor Red
    $failures | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    exit 1
}

Write-Host "OK: no staged secret leaks detected"
exit 0
