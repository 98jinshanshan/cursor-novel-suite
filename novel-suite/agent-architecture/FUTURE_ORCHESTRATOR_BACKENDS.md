# 未来可选编排后端（F2–F5 路线）

F1 确立：**当前核心保持 Skills-first / CLI / MCP 轻量 OS**；下列后端均为 **可选增强**，须单独 ADR + 安全评审。

## 阶段路线图

| 阶段 | 内容 | 是否写代码 |
| --- | --- | --- |
| **F1** | Agent 架构显性化（本文档包） | ❌ 仅文档 |
| **F2** | Workflow Contract Schema 文档与样例包 | 文档 + 可选 JSON schema |
| **F3** | Trace/State 最小记录规格包 | 规格 + 可选 CLI append |
| **F4** | LangGraph 可选 PoC **设计包**（不立刻实现） | 设计为主 |
| **F5** | RAG/素材库后端候选研究包 | 研究文档 |

---

## LangGraph

**适合：** 状态机、长流程、可恢复编排、子图（立项→写作→审稿→视频→发布门禁）。

**不适合作为 F1 核心：** 重构 CLI/MCP 成本高；多 IDE 分发需额外桥接。

**引入时机：** F4 PoC — 例如将 `novel-pipeline` Phase 0–9 建模为持久化图；checkpointer 存仓内 SQLite。

**边界：** PoC 不得默认启用 P4/P5 节点。

---

## OpenAI Agents SDK

**适合：** 统一工具调用、handoff、session、trace、Guardrails；OpenAI 生态 agentic app。

**不适合现在：** 强绑定 OpenAI；与 Cursor/Codex/TRAE 多模型策略冲突。

**引入时机：** 若推出「云端统一 Agent Runtime」产品线，可作为 **可选托管层**，Skills 仍作源 SOP。

---

## LlamaIndex

**适合：** Story Bible、Asset Registry、章节向量检索、长上下文 RAG。

**不适合作为创作核心：** 编排与门禁仍应在 Novel Suite Core。

**引入时机：** F5 — 评估 `memory` 模块与 Qdrant 是否升级为 LlamaIndex 或保持轻量自研。

---

## CrewAI

**适合：** 专家团角色化（策划/编辑/审稿/导演/合规）— 与用户「圆桌」表达一致。

**不适合商业核心运行时：** 多 Agent 自动执行难与确定性 gate 对齐。

**引入时机：** 内部评审沙箱或「模拟专家团」实验；输出须过 `novel-review` gate。

---

## AutoGen

**适合：** 多 Agent 研究、事件驱动讨论、内部审计。

**不适合商业交付核心：** 可控性弱于 SOP + CLI。

**引入时机：** 非面向客户的运行时；可与 AI_Workspace 评审流程结合。

---

## Semantic Kernel

**适合：** 微软/Azure 企业集成场景。

**不适合当前：** Python 多 IDE 工具包主线；绑定过重。

**引入时机：** 仅当企业客户明确要求 Azure 栈时评估插件层。

---

## n8n / Make / Zapier

**适合：** 发布后排期、CRM、通知、运营自动化。

**不适合创作核心：** 非分镜/写作/审稿主路径。

**引入时机：** C9/C10 商业交付后的 **运营附录**，不替代 `novel-suite/core/workflows/`。

---

## MCP 的定位

MCP 不是「待替换的临时方案」，而是 **Agent 工具暴露标准**（已具备）。未来编排后端应 **调用** MCP/CLI，而非取代 Skills 与 Result Contract。

---

## 决策检查清单（引入任何后端前）

- [ ] 多 IDE 分发是否仍可用？
- [ ] P0–P5 权限是否映射？
- [ ] `COMMERCIAL_RELEASE_GATE` 是否仍默认不允许？
- [ ] 是否新增 AGPL/云服务依赖？
- [ ] 是否有 F3 trace 可追溯？
- [ ] C8 安全评审（若含 P4/P5）
