# TRAE CN / SOLO — Agent 对话与 smoke 验证

**状态：** 仓内 smoke ✅；SOLO 自定义 Agent 见排障  
**主入口：** [AGENTS.md](../../AGENTS.md)  
**SOLO Prompt 模板：** [solo-agent-prompt.md](../../cursor-novel-writer/platforms/trae/solo-agent-prompt.md)

---

## 核心：SOLO「上传 Agent」≠ 安装 Skills

| 概念 | 作用 |
| --- | --- |
| SOLO 自定义 Agent | 对话 UI 里的角色 / system prompt |
| `.trae/skills/` | 后台 `SKILL.md` 工具库（必须单独安装） |

---

## 正确安装（任意路径，结构固定）

```powershell
# Novel Suite 根（含 .novel-suite-root，路径任意）
powershell -File platforms/install-skills.ps1 -Agents trae-cn
py -3 cursor-novel-writer/engine/novel_cli.py suite doctor
```

验证：

```powershell
Get-ChildItem .trae\skills\novel-pipeline\SKILL.md
Get-ChildItem .trae\skills\novel-market-scan\scripts\intel_scan.py
```

### SOLO 自定义 Agent（可选）

复制 [solo-agent-prompt.md](../../cursor-novel-writer/platforms/trae/solo-agent-prompt.md) 中的 System Prompt 到 SOLO Agent 配置。

---

## Agent 对话 smoke

| 步骤 | 输入 | 预期 |
| --- | --- | --- |
| 0 | `请运行 novel suite doctor` | 全部 OK |
| 1 | `#novel-market-scan 执行本周 intel scan` | `intel/radar/*.md` |
| 2 | `#novel-pipeline 显示 pipeline status` | Phase 列表 |
| 3 | `写 active 小说下一章` | 章节草稿 |

---

## 排障清单（「找不到技能」）

1. IDE 工作区是否为 **Novel Suite 根**（含 `.novel-suite-root`）？  
2. 是否运行 `platforms/install-skills.ps1`（不是只上传 Agent）？  
3. `novel suite doctor` 哪些项 FAIL？  
4. `.trae/skills/novel-market-scan/scripts/intel_scan.py` 是否存在？（旧拷贝会缺）  
5. 是否只打开了 `cursor-novel-writer/` 子目录？

---

## 与 Cursor / Qoder 对比

三端本质相同：**Skills 目录 + Novel Suite 根 + 完整 monorepo**。  
SOLO 多一层 Agent 上传 UI，更容易混淆。

---

## 检查项

| 项 | 结果 | 日期 |
| --- | --- | --- |
| install-skills.ps1 | ✅ | 2026-06-01 |
| suite doctor | 待 UI 补录 | — |
| SOLO Agent + Skills 联调 | ⏳ 待补 | — |
