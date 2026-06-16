# 可选 API 适配器

| 文件 | 用途 | 依赖 | 环境变量 |
| --- | --- | --- | --- |
| [openai_image.py](./openai_image.py) | 分镜静帧 / 封面图 | `openai` | `OPENAI_API_KEY` |
| [comfyui_render.py](./comfyui_render.py) | ComfyUI 视觉后端（L2：UI→API 转换 + 入队） | ComfyUI HTTP API | `COMFYUI_URL`, `COMFYUI_WORKFLOW_JSON` |
| [comfyui_dynamic_comic.md](./comfyui_dynamic_comic.md) | 动态漫对接说明 | — | 见文档 |
| [seedance.md](./seedance.md) | Replicate Seedance 视频 B-roll | Replicate CLI / HTTP | `REPLICATE_API_TOKEN` |

## 调用顺序（drama 场景）

1. 用户提供的 `assets/` 图片
2. `comfyui_render.py`（`visual_backend=comfyui`，需本地 ComfyUI）
3. `openai_image.py` 生成静帧
4. `make_title_card.py` 文字卡（本地，免费）
5. Seedance（见 seedance.md，可选）

## 本地默认路径

不配置任何 API 时，pipeline 使用 **edge-tts + Ken Burns + 文字卡**，零成本可跑通。

**ComfyUI Desktop 连通测试（端口以设置为准，常见 8000）：**

```powershell
cd G:\CURSOR
.\cursor-novel-video\platforms\comfyui-smoke.ps1 check    # 一键连通测试
.\cursor-novel-video\platforms\comfyui-smoke.ps1 image    # 出一张测试图 (.png)
.\cursor-novel-video\platforms\comfyui-smoke.ps1 video    # 悬疑 Ch1 完整成片
```

**注意：** 只复制以 `cd` / `.\` / `py` 开头的行；不要把 `PS G:\CURSOR>` 或 `OK: ...` 输出贴回终端。
