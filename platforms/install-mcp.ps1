# Install Novel Suite MCP for Cursor — copy config + ensure mcp SDK
param([switch]$Force)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_suite-common.ps1"

$SuiteRoot = Get-SuiteRoot -StartDir $PSScriptRoot
$Example = Join-Path $SuiteRoot ".cursor\mcp.example.json"
$Target = Join-Path $SuiteRoot ".cursor\mcp.json"

Write-Host "Novel Suite root: $SuiteRoot"

try {
    py -3 -c "import mcp" 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "mcp not installed" }
    Write-Host "mcp SDK: OK"
} catch {
    Write-Host "Installing mcp SDK..."
    py -3 -m pip install mcp
}

if (-not (Test-Path $Example)) {
    throw "Missing $Example — run from a complete Novel Suite checkout."
}

if ((Test-Path $Target) -and -not $Force) {
    Write-Host ".cursor\mcp.json already exists; use -Force to overwrite"
} else {
    New-Item -ItemType Directory -Force -Path (Split-Path $Target) | Out-Null
    Copy-Item $Example $Target -Force
    Write-Host "MCP configured: $Target"
}

Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Restart Cursor"
Write-Host "  2. Settings -> MCP -> verify 'novel-suite' server"
Write-Host "  3. Agent can call auth.login / publish.upload tools"
