# ComfyUI Adapter (VideoRender-2R)

Localhost-only HTTP client + workflow registry for Novel Suite ch02 ComfyUI renders.

## Commands

```powershell
Set-Location G:\CURSOR
$env:PYTHONPATH="G:\CURSOR\src"

.\.venv\Scripts\python.exe tools\comfyui-adapter\comfyui_client.py system-stats --url http://127.0.0.1:8188 --json
.\.venv\Scripts\python.exe tools\comfyui-adapter\comfyui_client.py object-info --url http://127.0.0.1:8188 --json
.\.venv\Scripts\python.exe tools\comfyui-adapter\workflow_registry.py --url http://127.0.0.1:8188
.\.venv\Scripts\python.exe tools\video-render\render_ch02_comfyui.py --json
```

## Boundaries

- URLs: `127.0.0.1` / `localhost` only
- No auto model/node download
- Long history → `.tmp/comfyui-adapter/`
- Terminal: summary only

## Related

- `cursor-novel-video/adapters/comfyui_workflow.py` — minimal txt2img API workflow
- `skills/doc-router/SKILL.md` — preflight before bulk doc reads
