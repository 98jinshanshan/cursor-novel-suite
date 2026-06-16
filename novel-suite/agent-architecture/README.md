# Novel Suite Agent 架构（F1）

> **Novel Suite 当前核心不是绑定单一 Agent SDK，而是采用 Skills-first / CLI-backed / MCP-exposed / JSON Result Contract / Multi-IDE Rules Pack 的轻量 Agent OS 架构。**

## 这是什么？

Novel Suite 的 Agent 架构是一套 **可跨 IDE 分发** 的内容生产操作系统：

- **Skills-first**：用户通过 Agent 对话触发 Skill（`cursor-novel-writer/skills/`、`cursor-novel-video/skills/`），而非手敲 CLI。
- **CLI-backed**：引擎在 `src/novel_suite/` 与 legacy `novel_cli.py` / `video_cli.py` 中实现，Agent 后台调用。
- **MCP-exposed**：部分能力通过 `novel_suite.mcp_server` 暴露为 MCP tools（product、auth、publish 等）。
- **JSON Result Contract**：统一 `status/code/message/artifacts/next_actions/details`（`src/novel_suite/core/result.py`）。
- **Multi-IDE Rules Pack**：`novel-suite/rules-packs/` 与 `.agent-rules/` 薄适配 Cursor/Codex/TRAE/Qoder/OpenClaw。

## 为什么不是「没有框架」？

常见误解是把「未安装 LangGraph/CrewAI」等同于「没有 Agent 架构」。实际上 Novel Suite 已具备：

| 能力 | 证据 |
| --- | --- |
| 对话入口 | 根目录 `AGENTS.md` |
| 工作流 SOP | `novel-suite/core/workflows/` |
| 门禁 Guardrails | `novel-suite/core/gates/`、`COMMERCIAL_RELEASE_GATE.md` |
| 工具契约 | CLI 子命令 + MCP tools |
| 多 IDE 分发 | B6 trial-cards、rules-packs |
| 可解析结果 | `Result` dataclass、`agent/protocol.py` |

这是 **自研轻量 Agent OS**，而非第三方框架缺失。

## 与主流框架的关系

| 框架/标准 | 关系 |
| --- | --- |
| **MCP** | **已采用** — 暴露工具给 IDE Agent |
| **OpenAI Agents SDK** | 未来可选统一 runtime；当前不绑定 |
| **LangGraph** | 未来可选编排后端（F4 PoC）；当前不迁移 |
| **CrewAI** | 可借鉴角色化评审概念；不作核心运行时 |
| **AutoGen** | 适合内部多 Agent 研究；不作商业核心 |
| **LlamaIndex** | 未来 RAG/Story Bible 候选（F5） |
| **n8n/Make/Zapier** | 商业运营自动化参考；非创作核心 |

## 阅读顺序

1. [AGENT_ARCHITECTURE.md](AGENT_ARCHITECTURE.md) — 分层与证据
2. [AGENT_FRAMEWORK_DECISION.md](AGENT_FRAMEWORK_DECISION.md) — ADR：为何不迁移
3. [AGENT_RUNTIME_CAPABILITY_MATRIX.md](AGENT_RUNTIME_CAPABILITY_MATRIX.md) — 能力对比矩阵
4. [AGENT_TOOL_PERMISSION_MODEL.md](AGENT_TOOL_PERMISSION_MODEL.md) — P0–P5 权限
5. [AGENT_TRACE_AND_STATE_MODEL.md](AGENT_TRACE_AND_STATE_MODEL.md) — 未来 trace/state
6. [FUTURE_ORCHESTRATOR_BACKENDS.md](FUTURE_ORCHESTRATOR_BACKENDS.md) — F2–F5 路线

## 当前阶段能做什么 / 不能做什么

| 能做 | 不能做 |
| --- | --- |
| Skills 驱动写作/审稿/视频规格流程 | 绑定单一第三方 Agent SDK |
| CLI/MCP 只读 product layer | 默认调用 ComfyUI/Runway/TTS 等 |
| dry-run adapter 生成本地 plan（C5） | 声称商业发布已合规 |
| 多 IDE Rules Pack 分发 | 保证五端 IDE 能力完全一致 |
| JSON Result 供 Agent 解析 | 无门禁的自动平台发布（P5） |

## 外部参考

- AI_Workspace 调研报告：`Agent框架调研与当前架构评审报告_20260611.md`
- 工程报告：[docs/NOVEL_SUITE_F1_AGENT_ARCHITECTURE_REPORT.md](../../docs/NOVEL_SUITE_F1_AGENT_ARCHITECTURE_REPORT.md)
