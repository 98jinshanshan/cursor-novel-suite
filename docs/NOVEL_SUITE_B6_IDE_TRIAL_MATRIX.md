# Novel Suite B6 — 多 IDE 试跑矩阵

**执行日期：** 2026-06-10  
**范围：** 本地 dry-run + 仓内 `.agent-rules/` 分发；**不**写入用户全局 IDE 目录、**不**启动 GUI。  
**商业发布：** 仍**不允许**（见 [COMMERCIAL_RELEASE_GATE.md](../COMMERCIAL_RELEASE_GATE.md)）。

## 矩阵总览

| # | 环境 | Rules Pack 源 | 入口文件 | B6 仓内目标 | Trial Card |
| --- | --- | --- | --- | --- | --- |
| 1 | Cursor | `novel-suite/rules-packs/cursor/` | `rules.md` | `.agent-rules/cursor/` | [trial-cards/cursor.md](../novel-suite/trial-cards/cursor.md) |
| 2 | Codex | `novel-suite/rules-packs/codex/` | `AGENTS.md` | `.agent-rules/codex/` | [trial-cards/codex.md](../novel-suite/trial-cards/codex.md) |
| 3 | TRAE CN | `novel-suite/rules-packs/trae-cn/` | `rules.md` | `.agent-rules/trae-cn/` | [trial-cards/trae-cn.md](../novel-suite/trial-cards/trae-cn.md) |
| 4 | Qoder | `novel-suite/rules-packs/qoder/` | `rules.md` | `.agent-rules/qoder/` | [trial-cards/qoder.md](../novel-suite/trial-cards/qoder.md) |
| 5 | OpenClaw | `novel-suite/rules-packs/openclaw/` | `rules.md` | `.agent-rules/openclaw/` | [trial-cards/openclaw.md](../novel-suite/trial-cards/openclaw.md) |
| 6 | Generic Agent | `novel-suite/rules-packs/generic-agent/` | `rules.md` | `.agent-rules/generic-agent/` | [trial-cards/generic-agent.md](../novel-suite/trial-cards/generic-agent.md) |

**分发脚本：** `platforms/install-rules-packs.ps1`  
**DryRun：** `-DryRun -Agents cursor,codex,trae-cn,qoder,openclaw,generic-agent`  
**仓内 Copy：** `-Copy -DestRoot .agent-rules`（**勿** `-UseIdeDirs`）

---

## 1. Cursor

| 项 | 内容 |
| --- | --- |
| 源路径 | `novel-suite/rules-packs/cursor/` |
| 入口 | `rules.md` |
| IDE 原生路径（仅说明，B6 不写入） | `.cursor/rules/novel-suite-core.mdc` 或引用仓库路径 |
| 安全命令 | `doctor --core-contracts`、`product validate/list/read` |
| 禁止命令 | `auth login`、`publish upload`、TTS/图像 API、采集 |
| 人工确认 | 发布、适配器启用、依赖安装、git push |
| 验收 | DryRun 通过；`.agent-rules/cursor/rules.md` 存在；trial card 四命令齐全 |

## 2. Codex

| 项 | 内容 |
| --- | --- |
| 源路径 | `novel-suite/rules-packs/codex/` |
| 入口 | `AGENTS.md` |
| IDE 原生路径（仅说明） | 项目根 `AGENTS.md` 或 Codex 工作区入口 |
| 安全命令 | 同上 |
| 禁止命令 | 自动发布/登录/TTS/图像；复制 Skill 原文 |
| 人工确认 | `pip install`、发布、适配器 |
| 验收 | `.agent-rules/codex/AGENTS.md` 存在 |

## 3. TRAE CN

| 项 | 内容 |
| --- | --- |
| 源路径 | `novel-suite/rules-packs/trae-cn/` |
| 入口 | `rules.md` |
| IDE 原生路径（仅说明） | `.trae/rules/` 或 TRAE 项目规则区 |
| 安全命令 | 同上 + 中文输出 |
| 禁止命令 | 平台发布、TTS、绘图、外发 |
| 人工确认 | 发布、删除、适配器启用 |
| 验收 | `.agent-rules/trae-cn/rules.md` 存在 |

## 4. Qoder

| 项 | 内容 |
| --- | --- |
| 源路径 | `novel-suite/rules-packs/qoder/` |
| 入口 | `rules.md` |
| IDE 原生路径（仅说明） | `.qoder/rules/` |
| 安全命令 | 同上 |
| 禁止命令 | 自动发布/采集 |
| 人工确认 | 发布、适配器 |
| 验收 | `.agent-rules/qoder/rules.md` 存在 |

## 5. OpenClaw

| 项 | 内容 |
| --- | --- |
| 源路径 | `novel-suite/rules-packs/openclaw/` |
| 入口 | `rules.md` |
| IDE 原生路径（仅说明） | 配合 `skills/openclaw-novel-suite/` |
| 安全命令 | 本地 CLI + 文件读写 |
| 禁止命令 | OAuth、浏览器采集、TTS/图像 API |
| 人工确认 | `publish`、`auth login`、`pip install` |
| 验收 | `.agent-rules/openclaw/rules.md` 存在 |

## 6. Generic Agent

| 项 | 内容 |
| --- | --- |
| 源路径 | `novel-suite/rules-packs/generic-agent/` |
| 入口 | `rules.md` |
| IDE 原生路径（仅说明） | system prompt / 项目指令 |
| 安全命令 | 同上 |
| 禁止命令 | 发布外发、第三方适配器默认启用 |
| 人工确认 | 全部高风险动作 |
| 验收 | `.agent-rules/generic-agent/rules.md` 存在 |

---

## 统一试跑任务（所有环境）

1. 加载本环境 rules pack + trial card。
2. 执行：
   - `novel-suite doctor --core-contracts --json`
   - `novel-suite product validate --json`
   - `novel-suite product list --json`
   - `novel-suite product read --category workflows --name chapter_writing --json`
3. 阅读 `novel-suite/examples/cold_case_echo/`，输出下一步计划（**不**调用 TTS/发布/API）。
4. 输出：已读文件、命令结果、**默认关闭**边界、**人工确认**项。

## 规格源

- 仓库 `novel-suite/` 为执行规格
- AI_Workspace_OS `小说视频工具链三项目评审_20260610` 为只读规格源
- 不复制 SOLO/Reasonix 真实正文

## 引用

- [NOVEL_SUITE_B6_EXECUTION_REPORT.md](./NOVEL_SUITE_B6_EXECUTION_REPORT.md)
- [novel-suite/trial-cards/README.md](../novel-suite/trial-cards/README.md)
- [novel-suite/rules-packs/README.md](../novel-suite/rules-packs/README.md)
