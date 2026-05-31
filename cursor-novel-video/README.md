# cursor-novel-video

小说章节 → 短视频 / 分场景叙事片。**Agent Skills 开放标准** + **CLI** + **可选 MCP**。

Monorepo 审计与目录规范：[docs/INDEX.md](../docs/INDEX.md)

融合项目：

- [video_skills](https://github.com/hexiaochun/video_skills)
- [super-video-maker-skill](https://github.com/Bomx/super-video-maker-skill)
- [mcp-video](https://github.com/KyaniteLabs/mcp-video)

## 安装 Skills

```bash
npx skills add <owner>/cursor-novel-video -a cursor -a qoder -a trae-cn -g -y
```

PowerShell: `.\platforms\install.ps1`

## 依赖

- Python 3.10+
- **FFmpeg**（PATH 中可用）
- `pip install -r requirements.txt`

## Skills

| Skill | 成片 |
| --- | --- |
| `video-chapter-summary` | 60–180s 章节摘要（MVP） |
| `video-scene-drama` | 2–5min 分场景叙事（进阶） |
| `video-export` | 多尺寸导出与 QC |

## CLI

```bash
# 摘要短视频（默认竖屏 9:16）
python engine/video_cli.py summary \
  --chapter ../cursor-novel-writer/my-novel/chapters/01_开篇.md

# 分场景叙事（逐段 TTS + 画面对齐，可加字幕）
python engine/video_cli.py drama \
  --chapter ../cursor-novel-writer/my-novel/chapters/01_开篇.md --subtitles
```

输出：`tmp/video_jobs/<job_id>/output/*.mp4`

## 输入约定

读取 [cursor-novel-writer](../cursor-novel-writer) 产出的 `chapters/*.md`，
或任意同结构 Markdown 章节。

## 可选 API

| 适配器 | 环境变量 |
| --- | --- |
| `adapters/openai_image.py` | `OPENAI_API_KEY` |
| `adapters/seedance.md` | `REPLICATE_API_TOKEN` |

无 API 时使用 **edge-tts + 标题卡片 + Ken Burns + FFmpeg**。

## MCP（可选）

`pip install mcp` 后运行 `python mcp/server.py`。工具：

- `render_summary` / `render_drama`
- `generate_subtitles` / `burn_subtitles`
- `qc_video`

复制 `platforms/cursor/mcp.example.json` 到 `.cursor/mcp.json` 启用。

## License

MIT
