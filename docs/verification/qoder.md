# Qoder 平台 — Agent 对话与 smoke 验证

**状态：** 最小 smoke 已完成（2026-06-01）  
**主入口：** [AGENTS.md](../../AGENTS.md)

## 一次性安装

在 **Novel Suite 根目录**（含 `.novel-suite-root`）：

```powershell
powershell -File platforms/install-skills.ps1 -Agents qoder
py -3 cursor-novel-writer/engine/novel_cli.py suite doctor
```

Skills：`.qoder/skills/`

## Agent 对话 smoke

| 步骤 | 输入 | 预期 |
| --- | --- | --- |
| 0 | `novel suite doctor` | 全部 OK |
| 1 | `按 novel-market-scan 执行本周 intel scan` | intel 产出 |
| 2 | `按 novel-pipeline 显示 pipeline status` | Phase 列表 |
| 3 | `继续写 active 小说下一章` | chapter 草稿 |

## 常见排障

| 现象 | 处理 |
| --- | --- |
| 找不到 skill | `suite doctor` → 重装 `platforms/install-skills.ps1` |
| 工作区错误 | 打开 Novel Suite 根，不要只开子文件夹 |

## 备注

- Option A wrapper 依赖完整 monorepo
- Agent 包 ≠ Skills 目录（与 TRAE 相同）
