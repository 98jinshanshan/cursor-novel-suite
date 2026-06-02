# TRAE CN / SOLO — Agent 对话与 smoke 验证

**状态：** NEC 矩阵已统一（2026-06-03）  
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

与 Cursor 相同，见 [NEC-smoke-matrix.md](./NEC-smoke-matrix.md)。

可选 SOLO Prompt：[solo-agent-prompt.md](../../cursor-novel-writer/platforms/trae/solo-agent-prompt.md)

## 平台实测

| 步骤 | 结果 | 日期 |
| --- | --- | --- |
| install-skills trae-cn | 待手填 | — |
| node sync + gate demo | 待手填 | — |
