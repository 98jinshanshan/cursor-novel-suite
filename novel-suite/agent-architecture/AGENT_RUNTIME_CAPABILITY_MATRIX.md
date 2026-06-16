# Agent Runtime 能力矩阵（F1）

图例：`已具备` / `部分具备` / `适合引入` / `不适合作为核心` / `待评估`

| 维度 | Novel Suite 当前 | OpenAI Agents SDK | LangGraph | CrewAI | AutoGen | Semantic Kernel | LlamaIndex | MCP | n8n/Make/Zapier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 多 IDE 分发 | **已具备** | 部分具备 | 部分具备 | 部分具备 | 部分具备 | 不适合作为核心 | 部分具备 | **已具备** | 不适合作为核心 |
| Skill/Prompt 复用 | **已具备** | 部分具备 | 部分具备 | 已具备 | 部分具备 | 部分具备 | 部分具备 | 部分具备 | 不适合作为核心 |
| CLI 工具调用 | **已具备** | 已具备 | 部分具备 | 部分具备 | 部分具备 | 部分具备 | 部分具备 | 已具备 | 部分具备 |
| MCP 暴露 | **已具备** | 已具备 | 待评估 | 待评估 | 待评估 | 待评估 | 待评估 | **已具备** | 不适合作为核心 |
| 状态持久化 | 部分具备 | 已具备 | **适合引入** | 部分具备 | 部分具备 | 部分具备 | 已具备 | 不适合作为核心 | 已具备 |
| 长流程恢复 | 部分具备 | 部分具备 | **适合引入** | 部分具备 | 部分具备 | 部分具备 | 部分具备 | 不适合作为核心 | 已具备 |
| 多 Agent 协作 | 部分具备 | 已具备 | 已具备 | **适合引入** | **适合引入** | 部分具备 | 部分具备 | 不适合作为核心 | 部分具备 |
| RAG/知识库 | 部分具备 | 部分具备 | 部分具备 | 部分具备 | 部分具备 | 部分具备 | **适合引入** | 不适合作为核心 | 不适合作为核心 |
| Guardrails/Gates | **已具备** | 已具备 | 部分具备 | 部分具备 | 部分具备 | 部分具备 | 部分具备 | 不适合作为核心 | 部分具备 |
| Tracing/Observability | 部分具备 | **已具备** | 已具备 | 部分具备 | 部分具备 | 部分具备 | 部分具备 | 部分具备 | 已具备 |
| Human-in-the-loop | **已具备** | 已具备 | 已具备 | 部分具备 | 部分具备 | 部分具备 | 部分具备 | 不适合作为核心 | 已具备 |
| 商业交付可控性 | **已具备** | 部分具备 | 部分具备 | 部分具备 | 不适合作为核心 | 部分具备 | 部分具备 | 部分具备 | 部分具备 |
| 第三方依赖风险 | **已具备**（低绑定） | 部分具备 | 部分具备 | 部分具备 | 部分具备 | 部分具备 | 部分具备 | 已具备 | 部分具备 |

## Novel Suite「已具备」说明

- **多 IDE**：`rules-packs/` × 6、`.agent-rules/`、trial-cards（B6）。
- **Skill 复用**：`cursor-novel-writer/skills/`、`novel-pipeline` 总控。
- **CLI**：`novel-suite` 统一入口；legacy 引擎兼容。
- **MCP**：`mcp_server.py` 注册 product/auth/publish 等。
- **Gates**：`core/gates/`、`COMMERCIAL_RELEASE_GATE`、C6/C7、`skip_gate` 禁止默认。
- **HITL**：发布/OAuth/外部工具须人工确认（README、adapter 默认关闭）。

## Novel Suite「部分具备」说明

- **状态持久化**：`novels/<slug>/task_plan.md`、`progress.json`、video `job_state.json`；无统一 `run_id`（F3）。
- **长流程恢复**：`video resume`、checkpoint；无图编排回放（F4）。
- **多 Agent**：专家团在文档/Skill 层模拟；非运行时 Crew。
- **RAG**：`memory` 模块 + Qdrant 可选；Story Bible 未统一 RAG 后端（F5）。
- **Tracing**：JSON Result Contract；无 OpenTelemetry/trace_id 规范（F3）。

## 结论

Novel Suite 在 **分发、门禁、商业可控、CLI/MCP** 维度已具备轻量 Agent OS 能力；**编排持久化、trace、RAG** 适合通过 F2–F5 渐进增强，而非 F1 整体迁移框架。
