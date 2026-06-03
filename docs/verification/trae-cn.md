# TRAE CN / SOLO — Agent 对话与 smoke 验证

**状态：** SOLO 引擎 + Agent NEC 验收通过（2026-06-03）  
**主入口：** [AGENTS.md](../../AGENTS.md)  
**统一验收表：** [NEC-smoke-matrix.md](./NEC-smoke-matrix.md)  
**SOLO 部署：** [solo-clone-checklist.md](./solo-clone-checklist.md)

## 核心：SOLO「上传 Agent」≠ 安装 Skills

| 概念 | 作用 |
| --- | --- |
| SOLO 自定义 Agent | 对话 UI / system prompt |
| `.trae/skills/` | Skills 工具库（须 `install-skills.ps1`） |

## 安装

```powershell
powershell -File platforms/install-skills.ps1 -Agents trae-cn
py -3 cursor-novel-writer/engine/novel_cli.py suite doctor
```

## NEC smoke

引擎命令与 Cursor/GitHub CI 相同；**SOLO 对话脚本**见：

- [solo-nec-dialogue.md](./solo-nec-dialogue.md)（推荐测试用）
- [solo-clone-checklist.md](./solo-clone-checklist.md)（安装 + 纠偏）

```powershell
py -3 cursor-novel-writer/engine/novel_cli.py suite doctor --agents trae-cn
py -3 cursor-novel-writer/engine/scripts/nec_cursor_smoke.py
py -3 cursor-novel-video/engine/scripts/nec_video_smoke.py
```

System Prompt：[solo-agent-prompt.md](../../cursor-novel-writer/platforms/trae/solo-agent-prompt.md)

## 平台实测

| 步骤 | 结果 | 日期 |
| --- | --- | --- |
| install-skills trae-cn | ✅ 13 skills | 2026-06-03 |
| nec smoke + pytest 38 | ✅ gaps `[]` | 2026-06-03 |
| node sync 1–9 demo | ✅ 全 complete | 2026-06-03 |
| Agent Read + Top3 摘要 | ✅ novel-market-scan | 2026-06-03 |
