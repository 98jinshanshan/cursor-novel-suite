# Cursor 平台 — 安装与 smoke 验证

**状态：** 部分实测（2026-05-31，Windows / Cursor）

**下一步：** [GitHub 发布](../standards/GITHUB-RELEASE.md) → [graphify 真机对照](../../cursor-novel-writer/docs/graphify-upstream-verification.md)

## 检查项

| 项 | 命令/操作 | 结果 | 日期 |
| --- | --- | --- | --- |
| novel export (demo-novel) | `py -3 engine/novel_cli.py export --project examples/demo-novel` | ✅ EPUB 生成 | 2026-05-31 |
| novel skill wrapper | `py -3 skills/novel-export/scripts/create_epub.py --project examples/demo-novel` | ✅ | 2026-05-31 |
| video summary + subtitles | `py -3 engine/video_cli.py summary --chapter .../01_试章.md --subtitles` | ✅ MP4 + SRT | 2026-05-31 |
| Skills 路径 | Cursor Settings → Skills | 待填 | — |
| `npx skills add`（writer） | 自 repo 根或子目录 | 待填 | — |
| `npx skills add`（video） | 同上 | 待填 | — |
| `platforms/install.ps1` | Windows | 待填 | — |
| graphify CLI 真机 | 见 graphify-upstream-verification.md | 待填 | — |

## 备注

- Python 3.13 + FFmpeg 8.0.1
- graphify CLI 未安装；offline 降级正常
