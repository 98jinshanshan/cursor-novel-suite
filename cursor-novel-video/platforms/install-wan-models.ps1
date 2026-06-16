# Install Wan 2.1 missing weights into ComfyUI model dirs (auto-detect from extra_model_paths.yaml).
#
# Usage:
#   .\cursor-novel-video\platforms\install-wan-models.ps1 -ProbeOnly
#   .\cursor-novel-video\platforms\install-wan-models.ps1 -InstallT2V
#   .\cursor-novel-video\platforms\install-wan-models.ps1 -InstallT2V -ComfyRoot "G:\ComfyUI"

param(
    [string]$ComfyRoot = "",
    [switch]$ProbeOnly,
    [switch]$InstallT2V,
    [switch]$LinkClipVisionAlias
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $RepoRoot

function Resolve-ComfyRoot {
    param([string]$Override)
    if ($Override) { return (Resolve-Path $Override).Path }
    $yaml = "G:\ComfyUI\models\extra_model_paths.yaml"
    if (Test-Path $yaml) {
        $line = Get-Content $yaml | Where-Object { $_ -match '^\s*base_path:\s*(.+)$' } | Select-Object -First 1
        if ($line -match 'base_path:\s*(.+)') {
            $p = $Matches[1].Trim()
            if (Test-Path $p) { return (Resolve-Path $p).Path }
        }
    }
    foreach ($c in @("G:\ComfyUI", "C:\ComfyUI")) {
        if (Test-Path $c) { return (Resolve-Path $c).Path }
    }
    throw "Cannot resolve ComfyUI root. Set -ComfyRoot or fix extra_model_paths.yaml"
}

$ComfyRoot = Resolve-ComfyRoot -Override $ComfyRoot
$ModelsRoot = Join-Path $ComfyRoot "models"

# Paths per G_ComfyUI extra_model_paths.yaml (NOT .cursor, NOT repo tmp)
$dirs = @{
    diffusion = Join-Path $ModelsRoot "diffusion_models"
    text_enc  = Join-Path $ModelsRoot "text_encoders"
    vae       = Join-Path $ModelsRoot "vae"
    clip_vis  = Join-Path $ModelsRoot "clip_vision"
}
foreach ($d in $dirs.Values) { New-Item -ItemType Directory -Force -Path $d | Out-Null }

function Test-RealFile($path) {
    if (-not (Test-Path $path)) { return $false }
    $item = Get-Item $path
    if ($item.LinkType -eq "SymbolicLink") {
        $target = $item.Target
        if ($target -is [array]) { $target = $target[0] }
        return (Test-Path $target) -and ((Get-Item $target).Length -gt 1MB)
    }
    return $item.Length -gt 1MB
}

$i2vPath = Join-Path $dirs.diffusion "wan2.1_i2v_480p_14B_fp8_e4m3fn.safetensors"
$t2vGlob = Get-ChildItem $dirs.diffusion -Filter "wan2.1_t2v*" -ErrorAction SilentlyContinue | Where-Object { $_.Length -gt 1MB } | Select-Object -First 1
$umt5Path = Join-Path $dirs.text_enc "umt5_xxl_fp8_e4m3fn_scaled.safetensors"
$vaePath = Join-Path $dirs.vae "wan_2.1_vae.safetensors"
$clipH = Join-Path $dirs.clip_vis "clip_vision_h.safetensors"
$clipAlt = Join-Path $dirs.clip_vis "CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"

Write-Host "==> Config: $ComfyRoot\models\extra_model_paths.yaml"
Write-Host "==> Install targets (ComfyUI standard):"
Write-Host "    diffusion_models  -> $($dirs.diffusion)"
Write-Host "    text_encoders     -> $($dirs.text_enc)"
Write-Host "    vae               -> $($dirs.vae)"
Write-Host "    clip_vision       -> $($dirs.clip_vis)"
Write-Host ""
Write-Host "==> Wan inventory:"
Write-Host ("    i2v_unet     {0}" -f (Test-RealFile $i2vPath))
Write-Host ("    t2v_unet     {0}" -f ($(if ($t2vGlob) { $t2vGlob.Name } else { "MISSING" })))
Write-Host ("    umt5         {0}" -f (Test-RealFile $umt5Path))
Write-Host ("    wan_vae      {0}" -f (Test-RealFile $vaePath))
Write-Host ("    clip_vision  {0}" -f ($(if (Test-RealFile $clipH) { "clip_vision_h" } elseif (Test-RealFile $clipAlt) { "CLIP-ViT-H-14 (alias ok)" } else { "MISSING" })))
Write-Host ""

$env:COMFYUI_URL = "http://127.0.0.1:8000"
$env:COMFYUI_ROOT = $ComfyRoot
py -3 cursor-novel-video/adapters/comfyui_wan_t2i.py --probe

if ($ProbeOnly) { exit 0 }

$t2vUrl = "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/diffusion_models/wan2.1_t2v_1.3B_fp16.safetensors"
$t2vOut = Join-Path $dirs.diffusion "wan2.1_t2v_1.3B_fp16.safetensors"

if ($InstallT2V) {
    if (-not $t2vGlob) {
        Write-Host "==> Downloading Wan T2V 1.3B (~2.6GB)"
        Write-Host "    URL:  $t2vUrl"
        Write-Host "    DEST: $t2vOut"
        Invoke-WebRequest -Uri $t2vUrl -OutFile $t2vOut
        $saved = (Get-Item $t2vOut).Length / 1GB
        Write-Host ("    OK: saved {0:N2} GB" -f $saved)
    } else {
        Write-Host "==> T2V already present: $($t2vGlob.FullName)"
    }
    Write-Host ""
    Write-Host "Re-probe: py -3 cursor-novel-video/adapters/comfyui_wan_t2i.py --probe"
}

if ($LinkClipVisionAlias -and -not (Test-RealFile $clipH) -and (Test-RealFile $clipAlt)) {
    Write-Host "==> Optional: clip_vision_h alias (adapter already uses CLIP-ViT-H-14 if missing)"
    try {
        New-Item -ItemType SymbolicLink -Path $clipH -Target $clipAlt -Force -ErrorAction Stop | Out-Null
        Write-Host "    OK: symlink created"
    } catch {
        Write-Host "    WARN: symlink skipped (need Admin). No action required — Wan adapter uses CLIP-ViT-H-14." -ForegroundColor Yellow
    }
}
