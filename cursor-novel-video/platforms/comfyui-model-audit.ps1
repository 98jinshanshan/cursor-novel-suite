# Deep audit of ComfyUI model library (reads G:\ComfyUI\models\extra_model_paths.yaml).
# Usage: .\cursor-novel-video\platforms\comfyui-model-audit.ps1

param(
    [string]$ComfyRoot = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $RepoRoot

if (-not $ComfyRoot) {
    $yaml = "G:\ComfyUI\models\extra_model_paths.yaml"
    if (Test-Path $yaml) {
        $m = Select-String -Path $yaml -Pattern "base_path:\s*(.+)" | Select-Object -First 1
        if ($m) { $ComfyRoot = $m.Matches.Groups[1].Value.Trim() }
    }
    if (-not $ComfyRoot) { $ComfyRoot = "G:\ComfyUI" }
}

$ModelsRoot = Join-Path $ComfyRoot "models"
Write-Host "==> ComfyUI root (from extra_model_paths.yaml): $ComfyRoot"
Write-Host "==> Models root: $ModelsRoot"
Write-Host ""

$folders = @(
    "checkpoints", "diffusion_models", "text_encoders", "vae", "clip_vision",
    "loras", "controlnet", "animatediff_models", "ipadapter", "insightface", "LLM"
)
$totalMb = 0
foreach ($name in $folders) {
    $dir = Join-Path $ModelsRoot $name
    if (-not (Test-Path $dir)) { continue }
    $files = Get-ChildItem $dir -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension -match '\.(safetensors|ckpt|pt|pth|bin|gguf|onnx)$' }
    if (-not $files) { continue }
    Write-Host "=== $name ==="
    foreach ($f in ($files | Sort-Object Length -Descending)) {
        $mb = [math]::Round($f.Length / 1MB, 1)
        $totalMb += $mb
        $sym = if ($f.LinkType -eq "SymbolicLink") { " [symlink]" } else { "" }
        $rel = $f.FullName.Replace("$ModelsRoot\", "")
        Write-Host ("  {0,9:N1} MB  {1}{2}" -f $mb, $rel, $sym)
    }
    Write-Host ""
}
Write-Host ("Total scanned weight files: ~{0:N0} GB" -f ($totalMb / 1024))
Write-Host ""
$env:COMFYUI_URL = "http://127.0.0.1:8000"
$env:COMFYUI_ROOT = $ComfyRoot
py -3 cursor-novel-video/adapters/comfyui_wan_t2i.py --probe
