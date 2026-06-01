# Install cursor-novel-writer skills (delegates to monorepo install-skills.ps1)
param(
    [string[]]$Agents = @("cursor", "qoder", "trae-cn"),
    [switch]$Global,
    [switch]$Copy
)

$SuiteInstall = Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) "platforms\install-skills.ps1"
if (-not (Test-Path $SuiteInstall)) {
    Write-Error "Missing $SuiteInstall — run from full monorepo clone."
}
& $SuiteInstall @PSBoundParameters
