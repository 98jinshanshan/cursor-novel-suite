# Novel Suite 合并报告：F4 PoC 设计 + F5 RAG 研究 + C11 反馈复盘

**日期：** 2026-06-01  
**任务：** 设计/研究/复盘层 — **无** LangGraph/RAG/telemetry 运行时。

---

## F4 LangGraph PoC 设计结论

- **仅设计**：`novel-suite/orchestrator-poc-design/`（11 篇 + 3 个 `*.design.json`）
- **PoC v0 流程**：`product validate` → `workflow-contract validate` → `commercial-release-candidate validate`
- **映射**：F2 workflow contract → 图节点；F3 trace → checkpoint 字段设计
- **安全**：P4/P5、A2+ **blocked**；`runtime_implementation=false`、`langgraph_installed=false`
- **依赖决策**：当前 **不安装** LangGraph；未来须用户确认 + 隔离 optional extra + C8 审查

## F5 RAG/素材库研究结论

- **仅研究**：`novel-suite/knowledge-backend-research/`（16 篇 + 对比矩阵）
- **五类候选**：Local Markdown index、SQLite FTS、LlamaIndex、Qdrant、Chroma
- **推荐序**：Markdown index → SQLite FTS →（暂缓）向量栈
- **No-Go**：当前不引入 embedding/ingestion/vector DB；不扫描 SOLO/Reasonix
- **域**：Story Bible、Asset Registry、Prompt Library 分层检索模型已文档化

## C11 反馈复盘结论

- **包路径**：`novel-suite/trial-feedback-review/`
- **10 类 category** + **6 层 revision_layers**（schema + 虚构 sample）
- **backlog**：5 条 demo 条目（C11-BL-001..005）
- **原则**：不上传、无真实 PII、不自动改 product 文件
- **衔接 C10**：`trial_feedback_form` → `feedback_classification`

---

## 为什么不实现真实 LangGraph/RAG/telemetry

| 原因 | 说明 |
| --- | --- |
| C9 门禁 | `verdict=blocked`，不宜扩展运行时 |
| 轻量 OS | F1 Skills/CLI/MCP 已覆盖 validate 链 |
| 可解释性 | 商业交付优先 FTS/路径索引而非黑盒向量 |
| 安全 | adapter/RAG 摄入需 C8 + 权利审查 |
| 本阶段定位 | 用户约定仅设计/研究/复盘 |

**推荐下一步继续停留在文档/交付层**（G1–G3），而非默认安装 LangGraph/LlamaIndex。

---

## 新增/修改文件清单

### F4

`orchestrator-poc-design/README.md` + 10 设计文档 + `examples/*.design.json` × 3

### F5

`knowledge-backend-research/README.md` + 15 研究文档

### C11

`trial-feedback-review/` 全套（schema、sample、backlog、6 修订规则等）

### 代码

- `src/novel_suite/core/future_backends.py`
- `src/novel_suite/cli.py` — `future-backends validate`, `trial-feedback-review validate`
- `src/novel_suite/core/product_layer.py` — validate 扩展
- `tests/test_future_backend_designs.py`（5 tests）
- `tests/test_trial_feedback_review.py`（5 tests）

### 索引

- `novel-suite/README.md`, `docs/INDEX.md`, `NOVEL_SUITE_IMPLEMENTATION_PLAN.md`

---

## 验证结果

| 命令 | 结果 |
| --- | --- |
| `future-backends validate --json` | FUTURE_BACKENDS_VALIDATE_OK |
| `trial-feedback-review validate --json` | TRIAL_FEEDBACK_REVIEW_VALIDATE_OK |
| `product validate` | PRODUCT_VALIDATE_OK |
| `trace-state validate` | OK |
| `multi-ide-trials validate` | OK |
| `workflow-contract validate` | OK |
| 专项 pytest | 10 passed |

---

## 未执行动作

- 未安装 LangGraph/LlamaIndex/Qdrant/Chroma 等依赖
- 未实现 runner/RAG/telemetry
- 未调用外部服务
- 未执行 adapter
- 未修改 SOLO/Reasonix
- 未将 `commercial_release_allowed` 改为 true
- 未发布/上传/外发

---

## 下一阶段建议（执行包级）

1. **G1**：产品交付总索引与冷启动上手包
2. **G2**：商业演示路线图与人工试用计划
3. **G3**：法律/权利/商业发布人工复核包
