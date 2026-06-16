# ADR：Agent 框架决策（F1）

**状态：** 已接受  
**日期：** 2026-06-01  
**决策者：** Novel Suite 工程 + AI_Workspace 专家团（文档化）

---

## 背景

Novel Suite 已运行 **Skills + CLI + MCP + JSON Result Contract + Multi-IDE Rules Pack** 架构（B1–C7、C5 dry-run）。外部常见建议是「必须使用 LangGraph / CrewAI / OpenAI Agents SDK」。本 ADR 显性化：**当前不迁移到单一第三方框架作为核心**。

参考：`Agent框架调研与当前架构评审报告_20260611.md`（AI_Workspace，只读）。

---

## 决策

**保持轻量自研 Agent OS 为核心**，将 LangGraph、OpenAI Agents SDK、LlamaIndex、CrewAI、AutoGen、Semantic Kernel 定位为 **未来可选后端或参考范式**，不在 F1 阶段引入依赖或重构。

---

## 不选择单一第三方框架作为当前核心的原因

| 框架 | 不迁移原因 |
| --- | --- |
| **LangGraph** | 重构成本高；会挤压 CLI/MCP 轻量路径；长流程编排可延后到 F4 PoC |
| **CrewAI** | 多 Agent 自动执行与确定性 SOP/门禁冲突；适合借鉴角色概念 |
| **AutoGen** | 事件驱动多 Agent 对话难控；适合研究而非商业交付核心 |
| **Semantic Kernel** | .NET/微软生态绑定；与现有多 IDE Python 工具链不匹配 |
| **LlamaIndex** | RAG 有价值但非当前阻塞；F5 再评估 Story Bible / 素材库 |
| **OpenAI Agents SDK** | 强绑定 OpenAI 生态；损害 Cursor/Codex/TRAE 等跨 IDE 分发 |

---

## 保留当前架构的原因

1. **多 IDE 交付**已是差异化优势（B6 trial-cards、6 套 rules-packs）。
2. **商业可控**：默认关闭 adapter + P0–P5 权限模型 + C6/C7 门禁。
3. **可测试**：`pytest -m "not ffmpeg"` + Result Contract 断言。
4. **规格与引擎分离**：`novel-suite/` 产品层 + `src/novel_suite/` 实现。
5. **MCP 已是开放工具标准**，无需再套一层 SDK。

---

## 未来何时可引入

| 框架 | 触发条件 | 阶段 |
| --- | --- | --- |
| LangGraph | 需要持久化长流程、可恢复编排、子图复用 | F4 PoC 设计 |
| OpenAI Agents SDK | 需要统一 cloud runtime、handoff、tracing | F4+ 评估 |
| LlamaIndex | Story Bible / Asset Registry RAG 成为瓶颈 | F5 研究 |
| CrewAI | 专家团角色化评审要自动化（仍须门禁） | 待评估 |
| AutoGen | 内部审查/研究沙箱 | 非商业核心 |
| n8n/Make | 客户运营自动化（发布、CRM） | 非创作核心 |

---

## 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 缺少统一编排/trace | F2 workflow contract schema；F3 trace/state 规格 |
| Agent 误调用 P4/P5 工具 | `AGENT_TOOL_PERMISSION_MODEL.md` + Skills 明示 |
| 与「主流框架」叙事差距 | 本目录显性化架构；F1 报告对外说明 |
| 长会话状态丢失 | F3 `run_id/trace_id` 最小模型；可选 LangGraph 后端 |

---

## 明确声明

- **当前不迁移到 LangGraph。**
- **当前不迁移到 CrewAI。**
- **当前不迁移到 AutoGen。**
- **当前不迁移到 Semantic Kernel。**
- **当前不迁移到 LlamaIndex 作为核心运行时。**

上述框架可作为后续可选后端或参考范式，须经 ADR 修订与 C8 安全评审（若涉及真实外部调用）。
