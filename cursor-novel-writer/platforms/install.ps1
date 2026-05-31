# Install cursor-novel-writer skills to multiple agents (PowerShell)
param(
    [string[]]$Agents = @("cursor", "qoder", "trae-cn"),
    [switch]$Global
)

$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$SkillsSrc = Join-Path $Root "skills"

$AgentPaths = @{
    "cursor"   = if ($Global) { "$env:USERPROFILE\.cursor\skills" } else { ".agents\skills" }
    "qoder"    = if ($Global) { "$env:USERPROFILE\.qoder\skills" } else { ".qoder\skills" }
    "trae-cn"  = if ($Global) { "$env:USERPROFILE\.trae-cn\skills" } else { ".trae\skills" }
}

foreach ($agent in $Agents) {
    if (-not $AgentPaths.ContainsKey($agent)) { continue }
    $destRoot = $AgentPaths[$agent]
    if (-not $Global) { $destRoot = Join-Path (Get-Location) $destRoot }
    New-Item -ItemType Directory -Force -Path $destRoot | Out-Null
    Get-ChildItem $SkillsSrc -Directory | ForEach-Object {
        $dest = Join-Path $destRoot $_.Name
        if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
        Copy-Item -Recurse $_.FullName $dest
        Write-Host "Installed $($_.Name) -> $dest ($agent)"
    }
}

Write-Host "Done. Prefer: npx skills add <repo> -a cursor -a qoder -a trae-cn -y"
