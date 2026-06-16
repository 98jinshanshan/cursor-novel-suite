# ComfyUI smoke test — copy ONLY this file's commands, never paste terminal output back.
# Usage:
#   .\cursor-novel-video\platforms\comfyui-smoke.ps1 check
#   .\cursor-novel-video\platforms\comfyui-smoke.ps1 image
#   .\cursor-novel-video\platforms\comfyui-smoke.ps1 video

param(
    [Parameter(Position = 0)]
    [ValidateSet("check", "image", "video", "motion-comic", "motion-drama")]
    [string]$Action = "check",

    [string]$ComfyUrl = "http://127.0.0.1:8000",
    [string]$Prompt = "悬疑刑侦，冷色调，动漫风格，雨夜警局封存库",
    [string]$OutputImage = "cursor-novel-video/tmp/comfyui-test.png",
    [string]$Project = "novels/novel-837dd4f1",
    [string]$Chapter = "chapters/01_卷宗亮了.md"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $RepoRoot

$env:COMFYUI_URL = $ComfyUrl

Write-Host "==> repo: $RepoRoot"
Write-Host "==> COMFYUI_URL=$($env:COMFYUI_URL)"
Write-Host "==> action: $Action"
Write-Host ""

switch ($Action) {
    "check" {
        py -3 cursor-novel-video/adapters/comfyui_render.py --check
    }
    "image" {
        # ComfyUI outputs PNG; use .png extension (not .mp4).
        py -3 cursor-novel-video/adapters/comfyui_render.py `
            --profile minimal `
            --prompt $Prompt `
            --output $OutputImage
        if (Test-Path $OutputImage) {
            Write-Host ""
            Write-Host "Image saved: $(Resolve-Path $OutputImage)"
        }
    }
    "video" {
        Write-Host "WARN: 'video' uses summary (single-image). Prefer: motion-comic" -ForegroundColor Yellow
        py -3 cursor-novel-video/engine/video_cli.py summary `
            --project $Project `
            --chapter $Chapter `
            --aspect 9:16 `
            --subtitles `
            --visual-backend comfyui `
            --comfyui-profile minimal
    }
    "motion-comic" {
        Write-Host "WARN: motion-comic uses Ken Burns; prefer motion-drama for platform master." -ForegroundColor Yellow
        $env:COMFYUI_STYLE = "realistic"
        py -3 cursor-novel-video/engine/video_cli.py motion-comic `
            --project $Project `
            --chapter $Chapter `
            --aspect 9:16 `
            --subtitles `
            --visual-backend comfyui `
            --comfyui-profile minimal
    }
    "motion-drama" {
        $env:COMFYUI_STYLE = "realistic"
        py -3 cursor-novel-video/engine/video_cli.py motion-drama `
            --project $Project `
            --chapter $Chapter `
            --aspect 9:16 `
            --subtitles `
            --visual-backend comfyui `
            --comfyui-profile minimal
    }
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "FAILED (exit $LASTEXITCODE). If you see WinError 10061:" -ForegroundColor Yellow
    Write-Host "  1) Start ComfyUI Desktop (port 8000 in Server Config)" -ForegroundColor Yellow
    Write-Host "  2) Open http://127.0.0.1:8000 in browser" -ForegroundColor Yellow
    Write-Host "  3) Re-run: .\cursor-novel-video\platforms\comfyui-smoke.ps1 check" -ForegroundColor Yellow
    exit $LASTEXITCODE
}
