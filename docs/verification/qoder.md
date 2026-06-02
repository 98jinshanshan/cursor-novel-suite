# Qoder 平台 — Agent 对话与 smoke 验证

**状态：** NEC 矩阵已统一（2026-06-03）  
**主入口：** [AGENTS.md](../../AGENTS.md)  
**统一验收表：** [NEC-smoke-matrix.md](./NEC-smoke-matrix.md)

## 一次性安装

```powershell
powershell -File platforms/install-skills.ps1 -Agents qoder
py -3 cursor-novel-writer/engine/novel_cli.py suite doctor
```

Skills 源：`cursor-novel-writer/skills/`（安装到 `.qoder/skills/`，工作区已隐藏）。

## NEC smoke

与 Cursor 相同命令，见 [NEC-smoke-matrix.md](./NEC-smoke-matrix.md)。

## 平台实测

| 步骤 | 结果 | 日期 |
| --- | --- | --- |
| install-skills | 待手填 | — |
| node sync demo | 待手填 | — |
