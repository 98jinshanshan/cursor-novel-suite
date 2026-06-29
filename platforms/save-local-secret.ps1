# Save API keys locally (gitignored). Never pass keys on the command line (shell history).
#
# Usage (interactive — recommended):
#   powershell -File platforms/save-local-secret.ps1 -Provider siliconflow
#
# Usage (stdin pipe — still local only):
#   'your-key-here' | powershell -File platforms/save-local-secret.ps1 -Provider siliconflow -FromStdin
#
# Load in Python:
#   from local_secrets import get_siliconflow_api_key

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("siliconflow", "ark", "openai")]
    [string]$Provider,

    [switch]$FromStdin,
    [switch]$ShowPathOnly
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $RepoRoot

if ($env:CI -eq "true" -or $env:GITHUB_ACTIONS -eq "true") {
    Write-Error "save-local-secret.ps1 is for local workstations only (CI blocked)."
}

$SecretsDir = Join-Path $RepoRoot "platforms\data\local-secrets"
New-Item -ItemType Directory -Force -Path $SecretsDir | Out-Null

$map = @{
    siliconflow = @{ file = "siliconflow.json"; env = "SILICONFLOW_API_KEY"; prefix = "sk-" }
    ark         = @{ file = "ark.json"; env = "ARK_API_KEY"; prefix = "" }
    openai      = @{ file = "openai.json"; env = "OPENAI_API_KEY"; prefix = "sk-" }
}
$cfg = $map[$Provider]
$OutFile = Join-Path $SecretsDir $cfg.file

function Get-SecretPlain {
    if ($FromStdin) {
        $raw = [Console]::In.ReadToEnd().Trim()
        if (-not $raw) { throw "Empty stdin" }
        return $raw
    }
    Write-Host "Paste $($cfg.env) (input hidden, Enter to confirm):" -ForegroundColor Cyan
    $sec = Read-Host -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr).Trim()
    } finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
}

function Test-ForbiddenFingerprint {
    param([string]$Plain)
    $fpPath = Join-Path $RepoRoot "platforms\secret-fingerprints.json"
    if (-not (Test-Path $fpPath)) { return }
    $fps = (Get-Content $fpPath -Raw | ConvertFrom-Json).forbidden_sha256
    $sha = [BitConverter]::ToString(
        [Security.Cryptography.SHA256]::Create().ComputeHash([Text.Encoding]::UTF8.GetBytes($Plain))
    ).Replace("-", "").ToLowerInvariant()
    foreach ($entry in $fps) {
        if ($sha -eq $entry.sha256) {
            Write-Warning "This key matches blocked fingerprint $($entry.id). Save locally only; never commit. Consider rotating at provider."
        }
    }
}

function Assert-NotInGitIndex {
    param([string]$Path)
    $rel = $Path.Replace($RepoRoot + "\", "").Replace("\", "/")
    $tracked = git ls-files --error-unmatch $rel 2>$null
    if ($LASTEXITCODE -eq 0) {
        throw "Refusing to write secrets to tracked path: $rel"
    }
}

$key = Get-SecretPlain
if (-not $key) { throw "Empty key" }
if ($cfg.prefix -and -not $key.StartsWith($cfg.prefix)) {
    Write-Warning "Key does not start with expected prefix '$($cfg.prefix)'"
}

Test-ForbiddenFingerprint -Plain $key
Assert-NotInGitIndex -Path $OutFile

$payload = @{
    provider    = $Provider
    env_var     = $cfg.env
    saved_at    = (Get-Date).ToUniversalTime().ToString("o")
    local_only  = $true
    key         = $key
} | ConvertTo-Json -Depth 3

Set-Content -Path $OutFile -Value $payload -Encoding UTF8 -NoNewline
# Restrict to current user (Windows ACL)
try {
    icacls $OutFile /inheritance:r /grant:r "$env:USERNAME:(R,W)" | Out-Null
} catch {
    Write-Warning "Could not tighten ACL on $OutFile"
}

Write-Host "OK: saved $($cfg.env) -> $OutFile" -ForegroundColor Green
Write-Host "  (gitignored under platforms/data/ — never commit)" -ForegroundColor DarkGray
if ($ShowPathOnly) { Write-Output $OutFile }
