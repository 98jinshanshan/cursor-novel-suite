# Cursor 平台 — 安装与 smoke 验证

**状态：** 部分实测（2026-05-31，Windows / Cursor）

**下一步：** [GitHub 发布](../standards/GITHUB-RELEASE.md) · Qoder/TRAE 预留

## 检查项

| 项 | 命令/操作 | 结果 | 日期 |
| --- | --- | --- | --- |
| novel export (demo-novel) | `py -3 engine/novel_cli.py export --project examples/demo-novel` | ✅ EPUB | 2026-05-31 |
| novel skill wrapper | `skills/novel-export/scripts/create_epub.py` | ✅ | 2026-05-31 |
| video summary + subtitles | `video_cli.py summary ... --subtitles` | ✅ | 2026-05-31 |
| graphifyy 安装 | `pip install graphifyy` | ✅ | 2026-05-31 |
| graphify update (demo) | `py -3 -m graphify update examples/demo-novel` | ✅ 69 nodes | 2026-05-31 |
| bridge status/query | `graphify_bridge.py status/query` | ✅ 对照后修复 | 2026-05-31 |
| GitHub push | `98jinshanshan/cursor-novel-suite` | ✅ main | 2026-05-31 |
| graphify-novel Skill | `npx skills add Anshler/graphify-novel` | 待填 | — |
| MCP example | `platforms/cursor/mcp.example.json` | 待填 | — |

## 备注

- **graphify-novel** 为 Agent Skill，非 CLI；底层 **graphifyy** → `py -m graphify`
- 对照表：[graphify-upstream-commands.md](../../cursor-novel-writer/docs/graphify-upstream-commands.md)
