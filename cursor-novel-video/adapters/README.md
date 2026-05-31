# 可选 API 适配器

| 文件 | 用途 | 依赖 | 环境变量 |
| --- | --- | --- | --- |
| [openai_image.py](./openai_image.py) | 分镜静帧 / 封面图 | `openai` | `OPENAI_API_KEY` |
| [seedance.md](./seedance.md) | Replicate Seedance 视频 B-roll | Replicate CLI / HTTP | `REPLICATE_API_TOKEN` |

## 调用顺序（drama 场景）

1. 用户提供的 `assets/` 图片
2. `openai_image.py` 生成静帧
3. `make_title_card.py` 文字卡（本地，免费）
4. Seedance（见 seedance.md，可选）

## 本地默认路径

不配置任何 API 时，pipeline 使用 **edge-tts + Ken Burns + 文字卡**，零成本可跑通。
