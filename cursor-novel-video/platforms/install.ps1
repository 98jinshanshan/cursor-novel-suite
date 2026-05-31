Copy-Item -Recurse (Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) "skills\*") ".agents\skills\" -Force
Write-Host "Installed to .agents/skills. Or: npx skills add <repo>/cursor-novel-video -a cursor -a qoder -a trae-cn -y"
