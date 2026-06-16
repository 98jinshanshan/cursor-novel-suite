# Remove legacy / duplicate ComfyUI + SD-WebUI weights.
# ComfyUI: G:\ComfyUI\models (from extra_model_paths.yaml)
# SD-WebUI: E:\AI\sd-webui\sd-webui-aki-v4 (override with -SdRoot)
#
#   .\cursor-novel-video\platforms\remove-legacy-models.ps1
#   .\cursor-novel-video\platforms\remove-legacy-models.ps1 -Execute
#   .\cursor-novel-video\platforms\remove-legacy-models.ps1 -IncludeSdLegacy   # also purge forbidden singles on E
#   .\cursor-novel-video\platforms\remove-legacy-models.ps1 -SdRoot "E:\AI\sd-webui\sd-webui-aki-v4" -Execute

param(
    [string]$ComfyRoot = "",
    [string]$SdRoot = "E:\AI\sd-webui\sd-webui-aki-v4",
    [switch]$IncludeSdLegacy,
    [switch]$SkipSdScan,
    [switch]$Execute
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $RepoRoot

if (-not $ComfyRoot) {
    $yaml = "G:\ComfyUI\models\extra_model_paths.yaml"
    if (Test-Path $yaml) {
        $line = Get-Content $yaml | Where-Object { $_ -match '^\s*base_path:\s*(.+)$' } | Select-Object -First 1
        if ($line -match 'base_path:\s*(.+)') { $ComfyRoot = $Matches[1].Trim() }
    }
    if (-not $ComfyRoot) { $ComfyRoot = "G:\ComfyUI" }
}

$ModelsRoot = Join-Path $ComfyRoot "models"
$ManifestDir = Join-Path $ComfyRoot "backup"
$ManifestPath = Join-Path $ManifestDir "deleted-models-manifest-2026-06.json"
New-Item -ItemType Directory -Force -Path $ManifestDir | Out-Null

$legacyBasenames = @(
    "Anything-V3.0.safetensors"
    "3Guofeng3_v32Light.safetensors"
    "3Guofeng3_v33.safetensors"
    "sd_xl_base_1.0.safetensors"
    "stable-audio-open-1.0.safetensors"
    "majicmixRealistic_v5.safetensors"
    "realisticVisionV13_v13.safetensors"
    "acestep_v1.5_turbo.safetensors"
    "3loraGuofeng3Lora_v32LoraBigLight.safetensors"
    "Moxin_10.safetensors"
    "hanfu_v29.safetensors"
    "elegantHanfuRuqun_v10.safetensors"
    "animevae.pt"
    "kl-f8-anime2.ckpt"
)

$comfyTargets = @(
    @{ Path = "checkpoints\Anything-V3.0.safetensors"; Reason = "anime; project forbidden"; ReDownload = "civitai/huggingface checkpoint" }
    @{ Path = "checkpoints\3Guofeng3_v32Light.safetensors"; Reason = "国漫; project forbidden"; ReDownload = "civitai" }
    @{ Path = "checkpoints\sd_xl_base_1.0.safetensors"; Reason = "SDXL unused in pipeline"; ReDownload = "huggingface stabilityai/stable-diffusion-xl-base-1.0" }
    @{ Path = "checkpoints\stable-audio-open-1.0.safetensors"; Reason = "audio unrelated"; ReDownload = "huggingface stabilityai/stable-audio-open-1.0" }
    @{ Path = "checkpoints\majicmixRealistic_v5.safetensors"; Reason = "redundant SD1.5 realistic"; ReDownload = "civitai majicmixRealistic" }
    @{ Path = "checkpoints\realisticVisionV13_v13.safetensors"; Reason = "superseded by RV5.1 fallback"; ReDownload = "civitai realisticVisionV13" }
    @{ Path = "diffusion_models\acestep_v1.5_turbo.safetensors"; Reason = "music model unrelated"; ReDownload = "huggingface ace-step" }
    @{ Path = "loras\3loraGuofeng3Lora_v32LoraBigLight.safetensors"; Reason = "国漫 lora"; ReDownload = "civitai" }
    @{ Path = "loras\Moxin_10.safetensors"; Reason = "anime lora"; ReDownload = "civitai" }
    @{ Path = "loras\hanfu_v29.safetensors"; Reason = "古风 lora"; ReDownload = "civitai" }
    @{ Path = "loras\elegantHanfuRuqun_v10.safetensors"; Reason = "古风 lora"; ReDownload = "civitai" }
    @{ Path = "vae\animevae.pt"; Reason = "anime vae"; ReDownload = "civitai animevae" }
    @{ Path = "vae\kl-f8-anime2.ckpt"; Reason = "anime vae"; ReDownload = "civitai" }
)

if (Test-Path (Join-Path $ModelsRoot "controlnet")) {
    Get-ChildItem (Join-Path $ModelsRoot "controlnet") -Filter "*.pth" -File | ForEach-Object {
        $comfyTargets += @{
            Path       = "controlnet\$($_.Name)"
            Reason     = "controlnet unused in motion-drama"
            ReDownload = "huggingface lllyasviel/ControlNet-v1-1"
        }
        $legacyBasenames += $_.Name
    }
}

foreach ($sub in @("rolling_clockwise", "rolling_anticlockwise")) {
    $p = Join-Path $ModelsRoot "animatediff_motion_lora\$sub"
    if (Test-Path $p) {
        $comfyTargets += @{
            Path        = "animatediff_motion_lora\$sub"
            Reason      = "git clone junk in models folder"
            ReDownload  = "re-clone if needed"
            IsDirectory = $true
        }
    }
}

$keep = @(
    "checkpoints\Realistic_Vision_V5.1_fp16-no-ema.safetensors  (SD emergency fallback)"
    "diffusion_models\wan2.1_i2v_*"
    "diffusion_models\wan2.1_t2v_*"
    "text_encoders\umt5_*"
    "vae\wan_2.1_vae.safetensors"
    "vae\vae-ft-mse-840000-ema-pruned.safetensors"
    "clip_vision\*"
    "animatediff_models\mm_sd_v15_v2.ckpt"
    "ipadapter\*"
    "insightface\*"
    "loras\ip-adapter-faceid-*"
)

function Get-WeightFiles {
    param([string]$Root, [string[]]$SubDirs)
    $ext = '\.(safetensors|ckpt|pt|pth|bin|gguf|onnx)$'
    $out = @()
    foreach ($sub in $SubDirs) {
        $dir = Join-Path $Root $sub
        if (-not (Test-Path $dir)) { continue }
        Get-ChildItem $dir -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Length -gt 1024 -and $_.Name -match $ext } |
            ForEach-Object { $out += $_ }
    }
    return $out
}

function New-DeleteEntry {
    param(
        [string]$FullPath,
        [string]$DisplayPath,
        [string]$Reason,
        [string]$ReDownload = "civitai/huggingface",
        [string]$Source = "comfyui",
        [bool]$IsDirectory = $false
    )
    return [ordered]@{
        full_path   = $FullPath
        path        = $DisplayPath
        reason      = $Reason
        re_download = $ReDownload
        source      = $Source
        IsDirectory = $IsDirectory
    }
}

function Add-TargetIfNew {
    param($List, $Entry)
    $key = $Entry.full_path.ToLower()
    if ($script:seenPaths.ContainsKey($key)) { return }
    $script:seenPaths[$key] = $true
    [void]$List.Add([pscustomobject]$Entry)
}

$script:seenPaths = @{}
$allTargets = [System.Collections.Generic.List[object]]::new()

foreach ($t in $comfyTargets) {
    $full = Join-Path $ModelsRoot $t.Path
    if (-not (Test-Path $full)) { continue }
    $isDir = $t.IsDirectory -or (Test-Path $full -PathType Container)
    $entry = New-DeleteEntry -FullPath $full -DisplayPath $t.Path -Reason $t.Reason `
        -ReDownload $t.ReDownload -Source "comfyui" -IsDirectory:$isDir
    Add-TargetIfNew $allTargets $entry
}

# --- SD-WebUI scan (E drive) ---
$sdSummary = @{ intra = 0; cross = 0; legacy = 0 }
if (-not $SkipSdScan -and (Test-Path $SdRoot)) {
    $sdDirs = @(
        "models\Stable-diffusion",
        "models\Lora",
        "models\VAE",
        "models\ControlNet",
        "models\ESRGAN"
    )
    $sdFiles = Get-WeightFiles -Root $SdRoot -SubDirs $sdDirs
    $comfyFiles = @()
    if (Test-Path $ModelsRoot) {
        Get-ChildItem $ModelsRoot -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Length -gt 1024 -and $_.Name -match '\.(safetensors|ckpt|pt|pth)$' } |
            ForEach-Object { $comfyFiles += $_ }
    }

    # Intra-E duplicates: same name + size -> keep shortest relative path
    $groups = $sdFiles | Group-Object { "{0}|{1}" -f $_.Name.ToLower(), $_.Length }
    foreach ($g in ($groups | Where-Object { $_.Count -gt 1 })) {
        $sorted = $g.Group | Sort-Object { $_.FullName.Replace($SdRoot + '\', '').Length }, FullName
        $keepFile = $sorted[0]
        foreach ($dup in $sorted | Select-Object -Skip 1) {
            $rel = $dup.FullName.Replace($SdRoot + '\', '')
            $entry = New-DeleteEntry -FullPath $dup.FullName -DisplayPath "sd-webui\$rel" `
                -Reason "E SD duplicate of $($keepFile.FullName.Replace($SdRoot + '\', ''))" `
                -ReDownload "already kept at $rel" -Source "sd-intra-dup"
            Add-TargetIfNew $allTargets $entry
            $sdSummary.intra++
        }
    }

    # Cross-location duplicates: exact name+size in ComfyUI -> delete E copy
    $comfyByKey = @{}
    foreach ($c in $comfyFiles) {
        $k = "{0}|{1}" -f $c.Name.ToLower(), $c.Length
        if (-not $comfyByKey.ContainsKey($k)) { $comfyByKey[$k] = $c }
    }
    foreach ($s in $sdFiles) {
        $k = "{0}|{1}" -f $s.Name.ToLower(), $s.Length
        if ($comfyByKey.ContainsKey($k)) {
            $rel = $s.FullName.Replace($SdRoot + '\', '')
            $crel = $comfyByKey[$k].FullName.Replace($ModelsRoot + '\', '')
            $entry = New-DeleteEntry -FullPath $s.FullName -DisplayPath "sd-webui\$rel" `
                -Reason "duplicate of ComfyUI $crel" -ReDownload "use ComfyUI copy" -Source "sd-comfy-dup"
            Add-TargetIfNew $allTargets $entry
            $sdSummary.cross++
        }
    }

    # Optional: purge legacy/forbidden basenames still on E (including last copy)
    if ($IncludeSdLegacy) {
        foreach ($s in $sdFiles) {
            if ($legacyBasenames -notcontains $s.Name) { continue }
            $rel = $s.FullName.Replace($SdRoot + '\', '')
            $entry = New-DeleteEntry -FullPath $s.FullName -DisplayPath "sd-webui\$rel" `
                -Reason "legacy/forbidden; already removed from ComfyUI pipeline" `
                -ReDownload "not needed for Wan motion-drama" -Source "sd-legacy"
            Add-TargetIfNew $allTargets $entry
            $sdSummary.legacy++
        }
    }
}

Write-Host "==> ComfyUI models: $ModelsRoot"
Write-Host "==> SD-WebUI root:  $(if (Test-Path $SdRoot) { $SdRoot } else { '(not found, SD scan skipped)' })"
Write-Host "==> Mode: $(if ($Execute) { 'DELETE' } else { 'PREVIEW (add -Execute to delete)' })"
if (-not $SkipSdScan -and (Test-Path $SdRoot)) {
    Write-Host "==> SD scan: intra-dup=$($sdSummary.intra) cross-comfy-dup=$($sdSummary.cross) legacy=$(if ($IncludeSdLegacy) { $sdSummary.legacy } else { 'off (add -IncludeSdLegacy)' })"
}
Write-Host ""
Write-Host "KEEP on ComfyUI:"
$keep | ForEach-Object { Write-Host "  $_" }
Write-Host ""

$manifest = [System.Collections.Generic.List[object]]::new()
$totalMb = 0
$bySource = @{}

foreach ($t in ($allTargets | Sort-Object { $_.source }, { $_.path })) {
    $full = $t.full_path
    if (-not (Test-Path $full)) { continue }
    $isDir = $t.IsDirectory -or (Test-Path $full -PathType Container)
    if ($isDir) {
        $sizeMb = (Get-ChildItem $full -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
    } else {
        $sizeMb = (Get-Item $full).Length / 1MB
    }
    $totalMb += $sizeMb
    $src = $t.source
    if (-not $bySource.ContainsKey($src)) { $bySource[$src] = 0 }
    $bySource[$src] += $sizeMb
    Write-Host ("  {0,9:N1} MB  [{1}] {2}" -f $sizeMb, $src, $t.path)
    if ($Execute) {
        if ($isDir) { Remove-Item $full -Recurse -Force }
        else { Remove-Item $full -Force }
        $manifest.Add([ordered]@{
            path        = $t.path
            source      = $t.source
            size_mb     = [math]::Round($sizeMb, 1)
            reason      = $t.reason
            re_download = $t.re_download
            deleted_at  = (Get-Date).ToString("o")
        })
    }
}

Write-Host ""
Write-Host ("Total to free: ~{0:N1} GB ({1} items)" -f ($totalMb / 1024), $allTargets.Count)
foreach ($kv in ($bySource.GetEnumerator() | Sort-Object Name)) {
    Write-Host ("  {0}: ~{1:N1} GB" -f $kv.Key, ($kv.Value / 1024))
}

if ($Execute) {
    $manifest | ConvertTo-Json -Depth 4 | Set-Content -Path $ManifestPath -Encoding UTF8
    Write-Host "Manifest: $ManifestPath"
    Write-Host "DONE: legacy/duplicate models removed."
} else {
    Write-Host ""
    Write-Host "Recommended commands:"
    Write-Host "  # Step 1: E duplicates only (~73 GB intra + cross-dup)"
    Write-Host "  .\cursor-novel-video\platforms\remove-legacy-models.ps1 -Execute"
    Write-Host ""
    Write-Host "  # Step 2: also purge forbidden legacy singles on E (~extra GB)"
    Write-Host "  .\cursor-novel-video\platforms\remove-legacy-models.ps1 -IncludeSdLegacy -Execute"
}
