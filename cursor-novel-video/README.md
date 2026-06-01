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

Monorepo 级市场情报：[intel/README.md](../intel/README.md)（P-1 选品）

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
# 绑定 registry 中的小说（推荐）
python engine/video_cli.py summary \
  --project ../novels/<slug> --chapter chapters/01_开篇.md

# 或直接给章节绝对/相对路径（自动推断 demo-novel / novels/<slug>）
python engine/video_cli.py summary \
  --chapter ../cursor-novel-writer/examples/demo-novel/chapters/01_试章.md
```

输出：`tmp/video_jobs/<job_id>/output/*.mp4`；登记在 `novels/_registry.json` → `video_jobs[]`（若在 registry 中）。

## 输入约定

读取 [cursor-novel-writer](../cursor-novel-writer) 产出的 `chapters/*.md`，
或任意同结构 Markdown 章节。

## 可选 API

| 适配器 | 环境变量 |
| --- | --- |
| `adapters/openai_image.py` | `OPENAI_API_KEY` |
| `adapters/seedance.md` | `REPLICATE_API_TOKEN` |

无 API 时使用 **edge-tts + 标题卡片 + Ken Burns + FFmpeg**。

## Quick Trigger 一览（VS-10）

| 用户说法（示例） | Skill / CLI |
| --- | --- |
| 章节摘要视频、短视频、60秒 | `video-chapter-summary` / `video_cli summary` |
| 分场景叙事、 drama 成片 | `video-scene-drama` / `video_cli drama` |
| 加字幕、烧录字幕 | `--subtitles` 或 `burn_subtitles.py` |
| 导出多尺寸、QC | `video-export` / `qc_video.py` |
| 竖屏 / 横屏 | `--aspect 9:16` / `16:9` / `1:1` |

脚本成功时 stdout 含 `RESULT: {...}` 行（SVM-06），Agent/MCP 应解析该 JSON。

## MCP（可选）

`pip install mcp` 后运行 `python mcp/server.py`。工具：

- `render_summary` / `render_drama`
- `generate_subtitles` / `burn_subtitles`
- `qc_video`

复制 `platforms/cursor/mcp.example.json` 到 `.cursor/mcp.json` 启用。

## License

MIT
