# Cursor 平台 — Agent 对话与 smoke 验证

**状态：** 部分实测（2026-05-31，Windows / Cursor）  
**主入口：** [AGENTS.md](../../AGENTS.md)（对话话术，非 CLI 优先）

## 一次性安装

在 **Novel Suite 根目录**（含 `.novel-suite-root`，路径任意）：

```bash
npx skills add ./cursor-novel-writer -a cursor -y
npx skills add ./cursor-novel-video -a cursor -y
py -3 cursor-novel-writer/engine/novel_cli.py suite doctor
```

或：

```powershell
powershell -File platforms/install-skills.ps1 -Agents cursor
```

Skills 目录：`.agents/skills/`、`.cursor/skills/`（junction 链接到源 skills，见 `platforms/install-skills.ps1`）。

## Agent 对话 smoke（推荐主路径）

| 步骤 | 在 Agent 对话输入 | 预期 |
| --- | --- | --- |
| 0 | `请运行 novel suite doctor 并解读结果` | 全部 OK |
| 1 | `请读取 novel-market-scan，执行 intel scan --period week 并总结 Top3 题材` | `intel/radar/*.md` + `intel/concepts/*.md` |
| 2 | `按 novel-pipeline 对 demo-novel 显示 pipeline status` | Phase 列表 |
| 3 | `把 demo 第1章做成 9:16 summary 视频加字幕` | MP4 输出 |

**说明：** 截图中的「Agent / Auto」是模式与模型选择，不是 Skill 下拉。

## 检查项（引擎层）

| 项 | 命令/操作 | 结果 | 日期 |
| --- | --- | --- | --- |
| suite doctor | `novel_cli.py suite doctor` | 待核对 | — |
| Skills 目录 | `.agents/skills/` 含 novel-pipeline 等 | 待核对 | — |
| pyright | `powershell -File .\typecheck.ps1` | ✅ | 2026-06-01 |

## 常见排障

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| Agent 说找不到 skill | 工作区不是 Novel Suite 根；或未装 Skills | `suite doctor` → `platforms/install-skills.ps1` |
| 脚本报 missing engine | 只打开了 `cursor-novel-writer/` 子目录 | 打开含 `.novel-suite-root` 的根目录 |
| Agent 只给命令不执行 | 模式/权限限制 | 明确说「请直接执行并汇报结果」 |

## 备注

- Cursor Rule：`.cursor/rules/novel-agent-entry.mdc`
- 根发现规范：[STRUCTURE-STANDARDS.md](../standards/STRUCTURE-STANDARDS.md) §1.4
