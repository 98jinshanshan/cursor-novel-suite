# Novel Suite — 产品对齐层

> 去 Cursor 化的产品文档、契约、Prompt Pack、Rules Pack 与适配器边界。  
> 工程实现见 `src/novel_suite/`；Agent Skills 见 `cursor-novel-writer/`、`cursor-novel-video/`。

**规格源（只读）：** AI_Workspace_OS `小说视频工具链三项目评审_20260610`  
**对齐报告：** [../NOVEL_SUITE_ALIGNMENT_REPORT.md](../NOVEL_SUITE_ALIGNMENT_REPORT.md)  
**实施计划：** [../NOVEL_SUITE_IMPLEMENTATION_PLAN.md](../NOVEL_SUITE_IMPLEMENTATION_PLAN.md)

---

## 目录

| 路径 | 用途 |
| --- | --- |
| [core/](core/) | 中立流程、契约、门禁（不绑定 IDE） |
| [prompt-packs/](prompt-packs/) | PP-001~003 自有 Prompt Pack |
| [rules-packs/](rules-packs/) | Cursor/Codex/TRAE/Qoder/OpenClaw/通用 Agent 薄规则 |
| [adapters/](adapters/) | TTS、图像、视频导出、平台发布 — **默认关闭** |
| [examples/](examples/) | 演示骨架（无原项目正文） |
| [video-production/](video-production/) | **C1+C2** AI 短剧生产契约、质量门禁、适配器（仅规格，无代码） |
| [agent-architecture/](agent-architecture/) | **F1** Agent 架构显性化：轻量 Agent OS、框架决策、权限/trace 模型 |
| [workflow-contracts/](workflow-contracts/) | **F2** Workflow Contract Schema 与 7 个样例契约 |
| [trace-state/](trace-state/) | **F3** Trace/State 最小记录规格（JSONL 样例，无采集器） |
| [multi-ide-trials/](multi-ide-trials/) | **C10** 多 IDE 试用脚本、Trial Cards、反馈回收 |
| [orchestrator-poc-design/](orchestrator-poc-design/) | **F4** LangGraph 可选 PoC **设计**（非运行时） |
| [knowledge-backend-research/](knowledge-backend-research/) | **F5** RAG/素材库后端候选 **研究**（非实现） |
| [trial-feedback-review/](trial-feedback-review/) | **C11** 试用反馈复盘与产品包修订规则 |
| [delivery-hub/](delivery-hub/) | **G1** 交付总索引与冷启动上手 |
| [demo-roadmap/](demo-roadmap/) | **G2** 商业演示路线与人工试用计划 |
| [legal-release-review/](legal-release-review/) | **G3** 法律/权利/商业发布人工复核 |
| [human-trial-runbook/](human-trial-runbook/) | **H1** 人工试用执行包（本地反馈） |
| [package-freeze-candidate/](package-freeze-candidate/) | **H2** 冻结候选与版本命名（非发布） |
| [legal-review-packet/](legal-review-packet/) | **H3** 律师/人工法律复核材料包 |
| [trial-results-intake/](trial-results-intake/) | **I1** 人工试用记录回填 |
| [freeze-version-alignment/](freeze-version-alignment/) | **I2** 冻结版本对齐（无 tag/release） |
| [legal-review-response-intake/](legal-review-response-intake/) | **I3** 法律意见回填（无自动关 blocker） |
| [first-trial-session-kit/](first-trial-session-kit/) | **J1** 首轮试用空白记录包（无伪造反馈） |
| [freeze-review-meeting/](freeze-review-meeting/) | **J2** 版本冻结评审会议包（无 tag/release） |
| [legal-review-meeting/](legal-review-meeting/) | **J3** 法律评审会议包（无自动关 blocker） |
| [trial-result-review/](trial-result-review/) | **K1** 人工试用结果承接（无伪造反馈） |
| [freeze-decision-record/](freeze-decision-record/) | **K2** 冻结会议结果承接（无 tag/release） |
| [legal-decision-record/](legal-decision-record/) | **K3** 法律会议结果承接（无自动关 blocker） |
| [trial-result-import-preflight/](trial-result-import-preflight/) | **L1** 试用结果导入预检（无真实导入） |
| [freeze-decision-import-preflight/](freeze-decision-import-preflight/) | **L2** 冻结决议导入预检（无 tag/release） |
| [legal-decision-import-preflight/](legal-decision-import-preflight/) | **L3** 法律决议导入预检（无关 blocker） |
| [trial-import-decision-record/](trial-import-decision-record/) | **M1** 试用预检决策记录（无真实导入） |
| [freeze-import-decision-record/](freeze-import-decision-record/) | **M2** 冻结预检决策记录（无 tag/release） |
| [legal-import-decision-board/](legal-import-decision-board/) | **M3** 法律预检评审委员会（不改 gate） |
| [trial-decision-fill-kit/](trial-decision-fill-kit/) | **N1** 试用决策人工填报（无伪造反馈） |
| [freeze-decision-fill-kit/](freeze-decision-fill-kit/) | **N2** 冻结决策人工填报（无 tag/release） |
| [legal-board-execution-kit/](legal-board-execution-kit/) | **N3** 法律评审委员会执行（不改 gate） |
| [docs/](docs/) | 源映射、实施顺序、迁移说明 |
| [agent-entry-menu/](agent-entry-menu/) | **W1** UI Agent 6 项菜单契约 |
| [server/](server/) | **W2** 本地 API Server 契约 |
| [ui-agent-workbench/](ui-agent-workbench/) | **W2** 零构建静态 Workbench |

## 产品边界

- [PRODUCT_BOUNDARY.md](PRODUCT_BOUNDARY.md) — 自有核心 / 可选适配器 / 外部参考
- [THIRD_PARTY_BOUNDARY.md](THIRD_PARTY_BOUNDARY.md) — AGPL/GPL/平台禁入

## 快速路径

```text
立项 → core/workflows/novel_project_init.md + prompt-packs/PP-001
写作 → core/workflows/chapter_writing.md
审稿 → core/gates/deai_review_gate.md + prompt-packs/PP-002
视频化 → core/workflows/novel_to_video.md + prompt-packs/PP-003
发布前 → core/gates/publishing_gate.md（人工确认）
```

## CLI / MCP 产品层查询（B2）

只读暴露 `novel-suite/` 文档与契约，**不**执行 TTS/图像/发布/API：

```powershell
novel-suite product list --json
novel-suite product read --category workflows --name chapter_writing --json
novel-suite product validate --json
```

MCP 工具：`product_list`、`product_read`、`product_validate`（见 `src/novel_suite/mcp_server.py`）。

## Agent Architecture（F1）

Novel Suite 采用 **Skills-first / CLI-backed / MCP-exposed / JSON Result Contract / Multi-IDE Rules Pack** 轻量 Agent OS，非单一第三方 Agent SDK 绑定。

- 入口：[agent-architecture/README.md](agent-architecture/README.md)
- 分层：[agent-architecture/AGENT_ARCHITECTURE.md](agent-architecture/AGENT_ARCHITECTURE.md)
- 框架决策 ADR：[agent-architecture/AGENT_FRAMEWORK_DECISION.md](agent-architecture/AGENT_FRAMEWORK_DECISION.md)
- 报告：[../docs/NOVEL_SUITE_F1_AGENT_ARCHITECTURE_REPORT.md](../docs/NOVEL_SUITE_F1_AGENT_ARCHITECTURE_REPORT.md)

## Workflow Contracts（F2）

统一工作流契约（非 LangGraph 运行时）：

```powershell
novel-suite workflow-contract validate --json
novel-suite product read --category workflow_contracts --name commercial_release_candidate --json
```

- 入口：[workflow-contracts/README.md](workflow-contracts/README.md)
- 报告：[../docs/NOVEL_SUITE_F2_WORKFLOW_CONTRACT_REPORT.md](../docs/NOVEL_SUITE_F2_WORKFLOW_CONTRACT_REPORT.md)

## Trace / State（F3）+ Multi-IDE Trials（C10）

```powershell
novel-suite trace-state validate --json
novel-suite multi-ide-trials validate --json
```

- F3：[trace-state/README.md](trace-state/README.md)
- C10：[multi-ide-trials/README.md](multi-ide-trials/README.md)
- 报告：[../docs/NOVEL_SUITE_F3_C10_TRACE_AND_TRIAL_REPORT.md](../docs/NOVEL_SUITE_F3_C10_TRACE_AND_TRIAL_REPORT.md)

## Future Backends & Feedback Review（F4/F5/C11）

```powershell
novel-suite future-backends validate --json
novel-suite trial-feedback-review validate --json
```

- F4 设计：[orchestrator-poc-design/README.md](orchestrator-poc-design/README.md)（**不**安装 LangGraph）
- F5 研究：[knowledge-backend-research/README.md](knowledge-backend-research/README.md)（**不**引入 RAG 运行时）
- C11 复盘：[trial-feedback-review/README.md](trial-feedback-review/README.md)
- 报告：[../docs/NOVEL_SUITE_F4F5_C11_BACKEND_AND_FEEDBACK_REPORT.md](../docs/NOVEL_SUITE_F4F5_C11_BACKEND_AND_FEEDBACK_REPORT.md)

## Delivery / Demo / Legal（G1–G3）

```powershell
novel-suite delivery-hub validate --json
novel-suite demo-roadmap validate --json
novel-suite legal-release-review validate --json
```

- G1 入口：[delivery-hub/start-here.md](delivery-hub/start-here.md)
- G2 演示：[demo-roadmap/demo_script_15min.md](demo-roadmap/demo_script_15min.md)
- G3 复核：[legal-release-review/README.md](legal-release-review/README.md)
- 报告：[../docs/NOVEL_SUITE_G1G2G3_DELIVERY_DEMO_LEGAL_REPORT.md](../docs/NOVEL_SUITE_G1G2G3_DELIVERY_DEMO_LEGAL_REPORT.md)

**商业发布仍 blocked** — G 阶段是交付整理，非发布。

## Human Trial / Freeze / Legal Packet（H1–H3）

```powershell
novel-suite human-trial-runbook validate --json
novel-suite package-freeze-candidate validate --json
novel-suite legal-review-packet validate --json
```

- H1：[human-trial-runbook/README.md](human-trial-runbook/README.md)
- H2：[package-freeze-candidate/README.md](package-freeze-candidate/README.md)（`0.1.0-demo-freeze-candidate`）
- H3：[legal-review-packet/README.md](legal-review-packet/README.md)
- 报告：[../docs/NOVEL_SUITE_H1H2H3_TRIAL_FREEZE_LEGAL_PACKET_REPORT.md](../docs/NOVEL_SUITE_H1H2H3_TRIAL_FREEZE_LEGAL_PACKET_REPORT.md)

## Intake / Alignment / Legal Response（I1–I3）

```powershell
novel-suite trial-results-intake validate --json
novel-suite freeze-version-alignment validate --json
novel-suite legal-review-response-intake validate --json
```

- 报告：[../docs/NOVEL_SUITE_I1I2I3_INTAKE_ALIGNMENT_LEGAL_RESPONSE_REPORT.md](../docs/NOVEL_SUITE_I1I2I3_INTAKE_ALIGNMENT_LEGAL_RESPONSE_REPORT.md)

## Trial / Freeze / Legal Meeting（J1–J3）

```powershell
novel-suite first-trial-session-kit validate --json
novel-suite freeze-review-meeting validate --json
novel-suite legal-review-meeting validate --json
```

- J1：[first-trial-session-kit/README.md](first-trial-session-kit/README.md)（空白表；`.tmp/novel-suite-j/`）
- J2：[freeze-review-meeting/README.md](freeze-review-meeting/README.md)
- J3：[legal-review-meeting/README.md](legal-review-meeting/README.md)
- 报告：[../docs/NOVEL_SUITE_J1J2J3_TRIAL_FREEZE_LEGAL_MEETING_REPORT.md](../docs/NOVEL_SUITE_J1J2J3_TRIAL_FREEZE_LEGAL_MEETING_REPORT.md)

## Result / Decision Records（K1–K3）

```powershell
novel-suite trial-result-review validate --json
novel-suite freeze-decision-record validate --json
novel-suite legal-decision-record validate --json
```

- K1：[trial-result-review/README.md](trial-result-review/README.md)（`.tmp/novel-suite-k/`）
- K2：[freeze-decision-record/README.md](freeze-decision-record/README.md)
- K3：[legal-decision-record/README.md](legal-decision-record/README.md)
- 报告：[../docs/NOVEL_SUITE_K1K2K3_RESULT_DECISION_RECORD_REPORT.md](../docs/NOVEL_SUITE_K1K2K3_RESULT_DECISION_RECORD_REPORT.md)

## Import Preflight（L1–L3）

```powershell
novel-suite trial-result-import-preflight validate --json
novel-suite freeze-decision-import-preflight validate --json
novel-suite legal-decision-import-preflight validate --json
```

- L1：[trial-result-import-preflight/README.md](trial-result-import-preflight/README.md)
- L2：[freeze-decision-import-preflight/README.md](freeze-decision-import-preflight/README.md)
- L3：[legal-decision-import-preflight/README.md](legal-decision-import-preflight/README.md)
- 报告：[../docs/NOVEL_SUITE_L1L2L3_IMPORT_PREFLIGHT_REPORT.md](../docs/NOVEL_SUITE_L1L2L3_IMPORT_PREFLIGHT_REPORT.md)

## Import Decision / Board（M1–M3）

```powershell
novel-suite trial-import-decision-record validate --json
novel-suite freeze-import-decision-record validate --json
novel-suite legal-import-decision-board validate --json
```

- M1：[trial-import-decision-record/README.md](trial-import-decision-record/README.md)
- M2：[freeze-import-decision-record/README.md](freeze-import-decision-record/README.md)
- M3：[legal-import-decision-board/README.md](legal-import-decision-board/README.md)
- 报告：[../docs/NOVEL_SUITE_M1M2M3_IMPORT_DECISION_BOARD_REPORT.md](../docs/NOVEL_SUITE_M1M2M3_IMPORT_DECISION_BOARD_REPORT.md)

## Decision Fill / Board Execution（N1–N3）

```powershell
novel-suite trial-decision-fill-kit validate --json
novel-suite freeze-decision-fill-kit validate --json
novel-suite legal-board-execution-kit validate --json
```

- N1：[trial-decision-fill-kit/README.md](trial-decision-fill-kit/README.md)（`.tmp/novel-suite-n/`）
- N2：[freeze-decision-fill-kit/README.md](freeze-decision-fill-kit/README.md)
- N3：[legal-board-execution-kit/README.md](legal-board-execution-kit/README.md)
- 报告：[../docs/NOVEL_SUITE_N1N2N3_DECISION_FILL_KIT_REPORT.md](../docs/NOVEL_SUITE_N1N2N3_DECISION_FILL_KIT_REPORT.md)

## UI Agent Workbench MVP（W1+W2）

```powershell
novel-suite agent-entry-menu validate --json
novel-suite agent-entry-menu list --json
novel-suite server validate --json
novel-suite server run --host 127.0.0.1 --port 8765
```

- W1 菜单：[agent-entry-menu/README.md](agent-entry-menu/README.md)（6 Agent 入口；商业 blocked）
- W2 API：[server/README.md](server/README.md) + `src/novel_suite/server/`
- W2 UI：[ui-agent-workbench/static/index.html](ui-agent-workbench/static/index.html)
- 报告：[../docs/NOVEL_SUITE_W1W2_UI_AGENT_WORKBENCH_MVP_REPORT.md](../docs/NOVEL_SUITE_W1W2_UI_AGENT_WORKBENCH_MVP_REPORT.md)

市场调研 Agent 仅 `writer scan --demo --json`；新书立项 UI 为 planned/disabled。  
`ip.to_short_drama` 为第二个 demo-runnable Agent（`ip-production-demo run`）。

## X 阶段（复测 + 短剧 Agent）

```powershell
novel-suite ip-production-demo validate --json
novel-suite ip-production-demo run --json
```

- Runbook：[ui-agent-workbench/runbook.md](ui-agent-workbench/runbook.md)
- OpenClaw 复测：[ui-agent-workbench/openclaw_retest_prompt.md](ui-agent-workbench/openclaw_retest_prompt.md)
- IP Demo：[ip-production-demo/README.md](ip-production-demo/README.md)
- 报告：[../docs/NOVEL_SUITE_X1X2X3_UI_WORKBENCH_REPORT.md](../docs/NOVEL_SUITE_X1X2X3_UI_WORKBENCH_REPORT.md)

## Y 阶段（结果卡片化 + 新手引导）

- UX 说明：[ui-agent-workbench/ux_notes.md](ui-agent-workbench/ux_notes.md)
- 报告：[../docs/NOVEL_SUITE_Y1Y2Y3_UI_RESULT_CARDS_REPORT.md](../docs/NOVEL_SUITE_Y1Y2Y3_UI_RESULT_CARDS_REPORT.md)

顶部推荐流程、摘要卡片、中文产物卡片；`novel.review` 已 demo-runnable（Y4）。

- 报告：[../docs/NOVEL_SUITE_Y4_NOVEL_REVIEW_DEMO_AGENT_REPORT.md](../docs/NOVEL_SUITE_Y4_NOVEL_REVIEW_DEMO_AGENT_REPORT.md)

## Z 阶段（本地 Demo 闭环验收 + Mobile 规划）

- Demo Success Gate：[ui-agent-workbench/demo_success_gate.md](ui-agent-workbench/demo_success_gate.md)
- Mobile 规划：[ui-agent-workbench/mobile_app_readiness_plan.md](ui-agent-workbench/mobile_app_readiness_plan.md)
- `release.preflight`：`planned-but-blocked`（见 [menu_items/release.preflight.json](agent-entry-menu/menu_items/release.preflight.json)）
- 报告：[../docs/NOVEL_SUITE_Z_LOCAL_DEMO_SUCCESS_GATE_REPORT.md](../docs/NOVEL_SUITE_Z_LOCAL_DEMO_SUCCESS_GATE_REPORT.md)

成功结论（仅此）：**本地 UI Agent Workbench Demo 闭环成立**。不实现 App/PWA；不扩 `asset.manage`。

## AA 阶段（Mobile-Ready PWA 输入契约与预览）

- 输入契约：[ui-agent-workbench/mobile_input_schemas.md](ui-agent-workbench/mobile_input_schemas.md)
- 产物预览：[ui-agent-workbench/mobile_artifact_preview.md](ui-agent-workbench/mobile_artifact_preview.md)
- 报告：[../docs/NOVEL_SUITE_AA_MOBILE_READY_PWA_REPORT.md](../docs/NOVEL_SUITE_AA_MOBILE_READY_PWA_REPORT.md)

窄屏响应式 + 只读输入区 + MD/JSON/CSV 轻量预览；仍 `verdict=blocked`。

## UserTrial-1（真实用户场景试用准备）

- 试用包：[user-trial-1/README.md](user-trial-1/README.md)
- 路径：Doctor → 章节审稿 → IP 转短剧 → 反馈表
- Workbench 入口：**真实试用指南（UserTrial-1）**
- 报告：[../docs/NOVEL_SUITE_USER_TRIAL_1_REPORT.md](../docs/NOVEL_SUITE_USER_TRIAL_1_REPORT.md)

## RealPipeline-2B（NVP 强制完整链 · 取代 RealGen-1）

- Active 书目：`novels/novel-837dd4f1`（冷案回声）
- 第 2 章：`chapters/02_双签.md`（3301 CJK · 林骁/陈琪）
- NVP 证据：`novels/novel-837dd4f1/reports/NVP-*.result.md`
- CLI：`novel_suite.cli realpipeline validate|run --project novels/novel-837dd4f1 --json`
- 总评：**C**（视频无 ch02 MP4；P9 export blocked）
- 报告：[../docs/NOVEL_SUITE_REALPIPELINE_2B_REPORT.md](../docs/NOVEL_SUITE_REALPIPELINE_2B_REPORT.md)

RealGen-1 旁路已废止，见 [realgen-demo/DEPRECATED.md](realgen-demo/DEPRECATED.md)。

## 离线 E2E Demo（B3）

- [examples/cold_case_echo/](examples/cold_case_echo/) — 自有虚构悬疑样例（非 SOLO/Reasonix 原文）
- 测试：`tests/video/test_cold_case_echo_e2e.py`（storyboard 在 `not ffmpeg` 套件；pipeline/gate 标记 `ffmpeg`）

## 状态

**内部对齐层 / 未商业发布。** 第三方适配器默认关闭；平台发布仍需人工确认；不复制外部 Skill 原文。
