# Novel Suite 阶段 F1 执行报告 — Agent 架构显性化与框架决策

**日期：** 2026-06-01  
**范围：** 仅文档与索引；不写代码、不新增依赖、不改运行逻辑。

---

## 本阶段目标

将 Novel Suite 当前真实 Agent 架构显性化，说明其为 **Skills-first / CLI-backed / MCP-exposed / JSON Result Contract / Multi-IDE Rules
Pack** 轻量 Agent OS，而非「没有框架」。

---

## 新增/修改文件

### 新增 — `novel-suite/agent-architecture/`（7 文件）

| 文件 | 说明 |
| --- | --- |
| `README.md` | 入口、阅读顺序、能/不能 |
| `AGENT_ARCHITECTURE.md` | 八层架构与证据路径 |
| `AGENT_FRAMEWORK_DECISION.md` | ADR：不迁移单一第三方框架 |
| `AGENT_RUNTIME_CAPABILITY_MATRIX.md` | 9 框架 × 13 维度矩阵 |
| `AGENT_TOOL_PERMISSION_MODEL.md` | P0–P5 权限映射 |
| `AGENT_TRACE_AND_STATE_MODEL.md` | trace/state 字段规格（无代码） |
| `FUTURE_ORCHESTRATOR_BACKENDS.md` | F2–F5 可选后端路线 |

### 修改 — 索引

| 文件 | 变更 |
| --- | --- |
| `novel-suite/README.md` | Agent Architecture 入口小节 |
| `docs/INDEX.md` | F1 报告与 agent-architecture 链接 |
| `NOVEL_SUITE_IMPLEMENTATION_PLAN.md` | 阶段 F + F2–F5 路线 |

### 报告与回执

- `docs/NOVEL_SUITE_F1_AGENT_ARCHITECTURE_REPORT.md`（本文件）
- AI_Workspace：`Cursor阶段F1执行回执.md`

---

## 当前架构一句话定义

> Novel Suite 是面向多 IDE 的 **轻量 Agent OS**：Skills 编排 SOP，CLI 确定性执行，MCP 暴露工具，
> JSON Result Contract 统一回传，Rules Pack 薄适配，门禁与商业审查层默认阻断 P4/P5。

---

## 为何不迁移单一第三方框架

| 框架 | 结论 |
| --- | --- |
| LangGraph | 适合 F4 编排 PoC；现在迁移成本高 |
| OpenAI Agents SDK | 适合未来 cloud runtime；现在损害多 IDE 中立 |
| CrewAI / AutoGen | 适合专家团实验；不适合商业确定性核心 |
| Semantic Kernel | Azure 绑定；非当前主线 |
| LlamaIndex | F5 RAG 候选；非编排核心 |

保留现有架构可维持：**多 IDE 交付、商业可控、pytest 可验证、adapter 默认关闭**。

---

## 与主流框架 / MCP 的关系

- **MCP**：已采用（`mcp_server.py`），作为工具暴露标准。
- **OpenAI Agents SDK / LangGraph**：未来可选后端，经 ADR + 安全评审引入。
- **CrewAI / AutoGen**：参考角色化与多 Agent 范式，不作 F1 运行时。
- **LlamaIndex**：Story Bible / RAG 候选（F5）。

外部参考已读：`Agent框架调研与当前架构评审报告_20260611.md`（AI_Workspace）。

---

## 权限模型摘要

| 等级 | 示例 | 规则 |
| --- | --- | --- |
| P0 | `product validate` | 可自动 |
| P1 | adapter dry-run | 可自动，`external_call_performed=false` |
| P2 | writer init, memory store | 仓内可逆写 |
| P3 | auth login | 人工确认 |
| P4 | ComfyUI/TTS/FFmpeg | 人工 + C8 |
| P5 | publish upload | 默认禁止 |

---

## Trace/State 后续建议（F3）

在现有 `Result` Contract 上叠加 `run_id` / `trace_id` JSONL 追加（仓内），再可选 LangGraph checkpointer（F4）。F1 仅字段定义，无代码。

---

## 验证结果

### 1. 文件存在性

| 项 | 结果 |
| --- | --- |
| `agent-architecture/` 7 文档 | ✅ |
| F1 报告 | ✅ |
| AI_Workspace 回执 | ✅ |

### 2. 关键词（抽样）

已在 `agent-architecture/README.md` 等文档中出现：

- Skills-first、CLI-backed、MCP-exposed、JSON Result Contract、Multi-IDE Rules Pack ✅
- LangGraph、OpenAI Agents SDK、MCP ✅
- P0 read-only、P5 publish/upload ✅

### 3. 可选只读工程命令

```text
novel-suite product validate --json → PRODUCT_VALIDATE_OK
```

---

## 未执行动作

- 未写 Python / JS / Shell 业务代码
- 未修改 `src/novel_suite/**`
- 未新增依赖（LangGraph/CrewAI 等）
- 未修改 SOLO / Reasonix
- 未调用外部服务
- 未发布 / 上传 / 外发
- 未跑大规模 pytest（F1 无代码变更）

---

## 下一阶段建议（执行包级）

1. **F2：** Workflow Contract Schema 文档与样例包
2. **F3：** Trace/State 最小记录规格包
3. **F4：** LangGraph 可选 PoC 设计包（不立刻实现）
4. **F5：** RAG/素材库后端候选研究包
