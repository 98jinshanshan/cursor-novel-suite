# Sprint 1.2 + Sprint 0 Day 2 — Qdrant Docker (127.0.0.1 only) + Python memory extras
#
#   .\platforms\install-memory-stack.ps1 -ProbeOnly
#   .\platforms\install-memory-stack.ps1 -InstallDocker
#   .\platforms\install-memory-stack.ps1 -InstallPython

param(
    [switch]$ProbeOnly,
    [switch]$InstallDocker,
    [switch]$InstallPython,
    [string]$QdrantUrl = "http://127.0.0.1:6333"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $RepoRoot

function Test-QdrantReachable {
    param([string]$Url)
    try {
        $r = Invoke-WebRequest -Uri "$Url/collections" -UseBasicParsing -TimeoutSec 5
        return $r.StatusCode -eq 200
    } catch {
        return $false
    }
}

Write-Host "==> Novel Suite memory stack (Sprint 1.2 / Sprint 0)"
Write-Host "==> Repo: $RepoRoot"
Write-Host ""

$dockerOk = $null -ne (Get-Command docker -ErrorAction SilentlyContinue)
$composeFile = Join-Path $PSScriptRoot "docker-compose.memory.yml"
$qdrantReachable = Test-QdrantReachable -Url $QdrantUrl

Write-Host "Docker CLI: $(if ($dockerOk) { 'yes' } else { 'no' })"
Write-Host "Compose file: $composeFile"
Write-Host "Qdrant ($QdrantUrl): $(if ($qdrantReachable) { 'reachable' } else { 'not reachable' })"
Write-Host ""

if ($InstallDocker) {
    if (-not $dockerOk) {
        throw "Docker not found. Install Docker Desktop or run Qdrant manually."
    }
    $dataDir = Join-Path $PSScriptRoot "data\qdrant_storage"
    New-Item -ItemType Directory -Force -Path $dataDir | Out-Null
    Write-Host "Starting Qdrant via docker compose (127.0.0.1:6333 only)..."
    docker compose -f $composeFile up -d
    Start-Sleep -Seconds 3
    $qdrantReachable = Test-QdrantReachable -Url $QdrantUrl
    Write-Host "Qdrant reachable: $qdrantReachable"
}

if ($InstallPython) {
    Write-Host "Installing Python extras: qdrant-client, sentence-transformers..."
    py -3 -m pip install -e ".[memory]"
}

if ($ProbeOnly -or (-not $InstallDocker -and -not $InstallPython)) {
    Write-Host ""
    Write-Host "CLI probe (requires --project):"
    Write-Host '  $env:QDRANT_URL = "http://127.0.0.1:6333"'
    Write-Host '  py -3 -m novel_suite.cli memory probe --project cursor-novel-writer/examples/demo-novel --json'
    Write-Host ""
    Write-Host "Recommended setup:"
    Write-Host "  .\platforms\install-memory-stack.ps1 -InstallDocker -InstallPython"
    Write-Host '  $env:QDRANT_URL = "http://127.0.0.1:6333"'
    Write-Host '  $env:MEMORY_EMBED_BACKEND = "m3e"'
}

Write-Host ""
Write-Host "=== 端口绑定验证 ===" -ForegroundColor Cyan
Write-Host "以下命令应显示 127.0.0.1:6333（而非 0.0.0.0:6333 或 *:6333）"
Write-Host "> netstat -an | Select-String 6333"
Write-Host ""
Write-Host "Qdrant 管理界面：http://127.0.0.1:6333/dashboard"

if ($qdrantReachable) {
    Write-Host ""
    Write-Host "OK: Qdrant ready at $QdrantUrl"
} elseif ($InstallDocker) {
    Write-Host "WARN: Qdrant not reachable yet — wait and re-run -ProbeOnly"
}
