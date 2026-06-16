# 文档索引

本 Monorepo 的说明与审计文档统一放在 `docs/` 下。

## 审计报告

| 文档 | 层级 | 说明 |
| --- | --- | --- |
| [audit/2026-05-31-novel-suite.md](./audit/2026-05-31-novel-suite.md) | 第一层 | 工程现状、E2E、P0 bug |
| [audit/2026-05-31-reference-crosswalk.md](./audit/2026-05-31-reference-crosswalk.md) | 第二层 | 12 个 GitHub 参考项目交叉指标 |
| [audit/2026-06-01-workflow-validation-synthesis.md](./audit/2026-06-01-workflow-validation-synthesis.md) | 第三层 | Workflow 编排与验证/去 AI 合成 |
| [audit/2026-06-02-full-reference-gap-matrix.md](./audit/2026-06-02-full-reference-gap-matrix.md) | 第四层 | 十二项目全维度差距矩阵（含 D11/P-1） |
| [audit/2026-06-03-solo-ch01-入府-audit.md](./audit/2026-06-03-solo-ch01-入府-audit.md) | 试写审稿 | SOLO 第1章《入府》+ 一二三节拍格式说明 |
| [audit/2026-06-04-python-security-audit.md](./audit/2026-06-04-python-security-audit.md) | 安全 | Python 静态安全审查（security-best-practices） |
| [audit/2026-06-01-session-questions-inventory.md](./audit/2026-06-01-session-questions-inventory.md) | 会话复盘 | JSONL 全量提问清单（175→34 主题） |
| [audit/2026-06-01-session-lifecycle-reordered.md](./audit/2026-06-01-session-lifecycle-reordered.md) | 会话复盘 | 按项目生命周期重排 + 🔁 未闭环标记 |
| [../intel/README.md](../intel/README.md) | P-1 | 市场情报目录（radar / concepts） |

## Novel Suite 产品对齐层（2026-06-10）

| 文档 | 说明 |
| --- | --- |
| [../novel-suite/README.md](../novel-suite/README.md) | **产品层入口**：Core / Prompt Pack / Rules Pack / Adapters |
| [../NOVEL_SUITE_ALIGNMENT_REPORT.md](../NOVEL_SUITE_ALIGNMENT_REPORT.md) | 工程 vs AI_Workspace_OS 规格对齐报告 |
| [../NOVEL_SUITE_IMPLEMENTATION_PLAN.md](../NOVEL_SUITE_IMPLEMENTATION_PLAN.md) | 实施计划与阶段 B 待办 |
| [../novel-suite/docs/AI_WORKSPACE_OS_SOURCE_MAP.md](../novel-suite/docs/AI_WORKSPACE_OS_SOURCE_MAP.md) | 文件→规格源映射 |
| [NOVEL_SUITE_B1_EXECUTION_REPORT.md](./NOVEL_SUITE_B1_EXECUTION_REPORT.md) | 阶段 B1 工程接入与测试记录 |
| [NOVEL_SUITE_B2B3_EXECUTION_REPORT.md](./NOVEL_SUITE_B2B3_EXECUTION_REPORT.md) | 阶段 B2+B3 产品层 CLI/MCP + cold_case_echo E2E |
| [NOVEL_SUITE_B4_EXECUTION_REPORT.md](./NOVEL_SUITE_B4_EXECUTION_REPORT.md) | 阶段 B4 商业合规硬化（ebooklib 拆分、发布门禁） |
| [NOVEL_SUITE_B6_IDE_TRIAL_MATRIX.md](./NOVEL_SUITE_B6_IDE_TRIAL_MATRIX.md) | 阶段 B6 多 IDE 试跑矩阵（6 Agent） |
| [NOVEL_SUITE_B6_EXECUTION_REPORT.md](./NOVEL_SUITE_B6_EXECUTION_REPORT.md) | 阶段 B6 执行记录与测试结果 |
| [../novel-suite/trial-cards/README.md](../novel-suite/trial-cards/README.md) | B6 试跑任务卡索引 |
| [../novel-suite/video-production/README.md](../novel-suite/video-production/README.md) | **C1+C2** AI 短剧生产契约与质量门禁规格层 |
| [NOVEL_SUITE_C1C2_VIDEO_PRODUCTION_SPEC_REPORT.md](./NOVEL_SUITE_C1C2_VIDEO_PRODUCTION_SPEC_REPORT.md) | C1C2 执行报告（仅文档，无代码） |
| [NOVEL_SUITE_C3_HANDOFF_SPEC_REPORT.md](./NOVEL_SUITE_C3_HANDOFF_SPEC_REPORT.md) | C3 外部专业软件 Handoff 文档包 |
| [NOVEL_SUITE_C4_PRODUCT_LAYER_REPORT.md](./NOVEL_SUITE_C4_PRODUCT_LAYER_REPORT.md) | **C4** video-production + handoff 只读 product layer 挂载 |
| [NOVEL_SUITE_C5_ADAPTER_SKELETON_REPORT.md](./NOVEL_SUITE_C5_ADAPTER_SKELETON_REPORT.md) | **C5** 默认关闭 adapter dry-run 原型（ComfyUI/OTIO/DaVinci） |
| [NOVEL_SUITE_C6C7_COMMERCIAL_PREFLIGHT_REPORT.md](./NOVEL_SUITE_C6C7_COMMERCIAL_PREFLIGHT_REPORT.md) | **C6+C7** 样例包商业前置 + 销售页/交付包审查 |
| [NOVEL_SUITE_C8C9_SECURITY_AND_RELEASE_GATE_REPORT.md](./NOVEL_SUITE_C8C9_SECURITY_AND_RELEASE_GATE_REPORT.md) | **C8+C9** Adapter 安全评审 + 商业候选包门禁 |
| [../novel-suite/video-production/adapter-security-review/README.md](../novel-suite/video-production/adapter-security-review/README.md) | C8 Adapter 安全评审规格 |
| [../novel-suite/commercial-release-candidate/README.md](../novel-suite/commercial-release-candidate/README.md) | C9 商业候选包与最终门禁 |
| [../novel-suite/video-production/commercial-review/README.md](../novel-suite/video-production/commercial-review/README.md) | C6 商业前置审查规格 |
| [../novel-suite/commercialization/README.md](../novel-suite/commercialization/README.md) | C7 销售页与交付包前置审查 |
| [NOVEL_SUITE_F1_AGENT_ARCHITECTURE_REPORT.md](./NOVEL_SUITE_F1_AGENT_ARCHITECTURE_REPORT.md) | **F1** Agent 架构显性化与框架决策 |
| [../novel-suite/agent-architecture/README.md](../novel-suite/agent-architecture/README.md) | F1 Agent OS 文档包入口 |
| [NOVEL_SUITE_F2_WORKFLOW_CONTRACT_REPORT.md](./NOVEL_SUITE_F2_WORKFLOW_CONTRACT_REPORT.md) | **F2** Workflow Contract Schema（含 C8/C9 复核） |
| [../novel-suite/workflow-contracts/README.md](../novel-suite/workflow-contracts/README.md) | F2 工作流契约文档与样例 |
| [NOVEL_SUITE_F3_C10_TRACE_AND_TRIAL_REPORT.md](./NOVEL_SUITE_F3_C10_TRACE_AND_TRIAL_REPORT.md) | **F3+C10** Trace/State 规格与多 IDE 试用包 |
| [../novel-suite/trace-state/README.md](../novel-suite/trace-state/README.md) | F3 Trace/State JSON Schema 与 JSONL 样例 |
| [../novel-suite/multi-ide-trials/README.md](../novel-suite/multi-ide-trials/README.md) | C10 多 IDE 试用脚本与反馈回收 |
| [NOVEL_SUITE_F4F5_C11_BACKEND_AND_FEEDBACK_REPORT.md](./NOVEL_SUITE_F4F5_C11_BACKEND_AND_FEEDBACK_REPORT.md) | **F4+F5+C11** PoC 设计 / RAG 研究 / 反馈复盘 |
| [../novel-suite/orchestrator-poc-design/README.md](../novel-suite/orchestrator-poc-design/README.md) | F4 LangGraph PoC 设计（非运行时） |
| [../novel-suite/knowledge-backend-research/README.md](../novel-suite/knowledge-backend-research/README.md) | F5 RAG 后端候选研究 |
| [../novel-suite/trial-feedback-review/README.md](../novel-suite/trial-feedback-review/README.md) | C11 试用反馈复盘与修订规则 |
| [NOVEL_SUITE_W1W2_UI_AGENT_WORKBENCH_MVP_REPORT.md](./NOVEL_SUITE_W1W2_UI_AGENT_WORKBENCH_MVP_REPORT.md) | **W1+W2** UI Agent Workbench MVP |
| [../novel-suite/agent-entry-menu/README.md](../novel-suite/agent-entry-menu/README.md) | W1 Agent 入口菜单 |
| [../novel-suite/ui-agent-workbench/README.md](../novel-suite/ui-agent-workbench/README.md) | W2 静态 Workbench |
| [../novel-suite/server/README.md](../novel-suite/server/README.md) | W2 API Server 契约 |
| [NOVEL_SUITE_X1X2X3_UI_WORKBENCH_REPORT.md](./NOVEL_SUITE_X1X2X3_UI_WORKBENCH_REPORT.md) | **X1+X2+X3** 复测路线 + ip.to_short_drama Agent |
| [../novel-suite/ip-production-demo/README.md](../novel-suite/ip-production-demo/README.md) | X3 IP 短剧离线 Demo |
| [NOVEL_SUITE_Y1Y2Y3_UI_RESULT_CARDS_REPORT.md](./NOVEL_SUITE_Y1Y2Y3_UI_RESULT_CARDS_REPORT.md) | **Y1+Y2+Y3** UI 结果卡片化与新手引导 |
| [../novel-suite/ui-agent-workbench/ux_notes.md](../novel-suite/ui-agent-workbench/ux_notes.md) | Y 阶段 UX 说明 |
| [NOVEL_SUITE_Y4_NOVEL_REVIEW_DEMO_AGENT_REPORT.md](./NOVEL_SUITE_Y4_NOVEL_REVIEW_DEMO_AGENT_REPORT.md) | **Y4** novel.review 离线 Demo Agent |
| [../novel-suite/novel-review-demo/README.md](../novel-suite/novel-review-demo/README.md) | Y4 审稿 Demo 包 |
| [NOVEL_SUITE_Z_LOCAL_DEMO_SUCCESS_GATE_REPORT.md](./NOVEL_SUITE_Z_LOCAL_DEMO_SUCCESS_GATE_REPORT.md) | **Z** 本地 Demo 闭环验收与 Mobile 规划 |
| [../novel-suite/ui-agent-workbench/demo_success_gate.md](../novel-suite/ui-agent-workbench/demo_success_gate.md) | Z Demo Success Gate |
| [../novel-suite/ui-agent-workbench/mobile_app_readiness_plan.md](../novel-suite/ui-agent-workbench/mobile_app_readiness_plan.md) | Z Mobile/App 前期规划 |
| [NOVEL_SUITE_AA_MOBILE_READY_PWA_REPORT.md](./NOVEL_SUITE_AA_MOBILE_READY_PWA_REPORT.md) | **AA** Mobile-Ready PWA 输入契约与预览 |
| [NOVEL_SUITE_HUMAN_FIX_1_REPORT.md](./NOVEL_SUITE_HUMAN_FIX_1_REPORT.md) | **Human-Fix-1** 真人试用反馈产品化修订 |
| [NOVEL_SUITE_USER_TRIAL_1_REPORT.md](./NOVEL_SUITE_USER_TRIAL_1_REPORT.md) | **UserTrial-1** 真实用户场景试用准备 |
| [NOVEL_SUITE_REALPIPELINE_2B_REPORT.md](./NOVEL_SUITE_REALPIPELINE_2B_REPORT.md) | **RealPipeline-2B** NVP 强制完整任务链（取代 RealGen-1） |
| [NOVEL_SUITE_REALGEN_1_REPORT.md](./NOVEL_SUITE_REALGEN_1_REPORT.md) | ~~RealGen-1~~ **已废止** |
| [../novel-suite/realgen-demo/DEPRECATED.md](../novel-suite/realgen-demo/DEPRECATED.md) | RealGen 旁路废止说明 |
| [../novel-suite/user-trial-1/README.md](../novel-suite/user-trial-1/README.md) | UserTrial-1 试用包 |
| [../novel-suite/ui-agent-workbench/mobile_input_schemas.md](../novel-suite/ui-agent-workbench/mobile_input_schemas.md) | AA 输入契约 |
| [../novel-suite/ui-agent-workbench/mobile_artifact_preview.md](../novel-suite/ui-agent-workbench/mobile_artifact_preview.md) | AA 产物预览规则 |
| [NOVEL_SUITE_G1G2G3_DELIVERY_DEMO_LEGAL_REPORT.md](./NOVEL_SUITE_G1G2G3_DELIVERY_DEMO_LEGAL_REPORT.md) | **G1+G2+G3** 交付索引、演示路线、法律复核 |
| [../novel-suite/delivery-hub/start-here.md](../novel-suite/delivery-hub/start-here.md) | G1 冷启动入口 |
| [../novel-suite/demo-roadmap/README.md](../novel-suite/demo-roadmap/README.md) | G2 演示路线图 |
| [../novel-suite/legal-release-review/README.md](../novel-suite/legal-release-review/README.md) | G3 法律/权利人工复核 |
| [NOVEL_SUITE_H1H2H3_TRIAL_FREEZE_LEGAL_PACKET_REPORT.md](./NOVEL_SUITE_H1H2H3_TRIAL_FREEZE_LEGAL_PACKET_REPORT.md) | **H1+H2+H3** 人工试用、冻结候选、律师材料 |
| [../novel-suite/human-trial-runbook/README.md](../novel-suite/human-trial-runbook/README.md) | H1 人工试用 runbook |
| [../novel-suite/package-freeze-candidate/README.md](../novel-suite/package-freeze-candidate/README.md) | H2 冻结候选 manifest |
| [../novel-suite/legal-review-packet/README.md](../novel-suite/legal-review-packet/README.md) | H3 法律复核材料包 |
| [NOVEL_SUITE_I1I2I3_INTAKE_ALIGNMENT_LEGAL_RESPONSE_REPORT.md](./NOVEL_SUITE_I1I2I3_INTAKE_ALIGNMENT_LEGAL_RESPONSE_REPORT.md) | **I1+I2+I3** 试用回填、版本对齐、法律回复 |
| [../novel-suite/trial-results-intake/README.md](../novel-suite/trial-results-intake/README.md) | I1 试用记录回填 |
| [../novel-suite/freeze-version-alignment/README.md](../novel-suite/freeze-version-alignment/README.md) | I2 冻结版本对齐 |
| [../novel-suite/legal-review-response-intake/README.md](../novel-suite/legal-review-response-intake/README.md) | I3 法律回复回填 |
| [NOVEL_SUITE_J1J2J3_TRIAL_FREEZE_LEGAL_MEETING_REPORT.md](./NOVEL_SUITE_J1J2J3_TRIAL_FREEZE_LEGAL_MEETING_REPORT.md) | **J1+J2+J3** 试用草案、冻结会议、法律会议 |
| [../novel-suite/first-trial-session-kit/README.md](../novel-suite/first-trial-session-kit/README.md) | J1 首轮试用空白记录包 |
| [../novel-suite/freeze-review-meeting/README.md](../novel-suite/freeze-review-meeting/README.md) | J2 版本冻结评审会议 |
| [../novel-suite/legal-review-meeting/README.md](../novel-suite/legal-review-meeting/README.md) | J3 法律评审会议 |
| [NOVEL_SUITE_K1K2K3_RESULT_DECISION_RECORD_REPORT.md](./NOVEL_SUITE_K1K2K3_RESULT_DECISION_RECORD_REPORT.md) | **K1+K2+K3** 试用/冻结/法律结果承接 |
| [../novel-suite/trial-result-review/README.md](../novel-suite/trial-result-review/README.md) | K1 试用结果承接 |
| [../novel-suite/freeze-decision-record/README.md](../novel-suite/freeze-decision-record/README.md) | K2 冻结会议结果承接 |
| [../novel-suite/legal-decision-record/README.md](../novel-suite/legal-decision-record/README.md) | K3 法律会议结果承接 |
| [NOVEL_SUITE_L1L2L3_IMPORT_PREFLIGHT_REPORT.md](./NOVEL_SUITE_L1L2L3_IMPORT_PREFLIGHT_REPORT.md) | **L1+L2+L3** 人工结果导入预检 |
| [../novel-suite/trial-result-import-preflight/README.md](../novel-suite/trial-result-import-preflight/README.md) | L1 试用结果导入预检 |
| [../novel-suite/freeze-decision-import-preflight/README.md](../novel-suite/freeze-decision-import-preflight/README.md) | L2 冻结决议导入预检 |
| [../novel-suite/legal-decision-import-preflight/README.md](../novel-suite/legal-decision-import-preflight/README.md) | L3 法律决议导入预检 |
| [NOVEL_SUITE_M1M2M3_IMPORT_DECISION_BOARD_REPORT.md](./NOVEL_SUITE_M1M2M3_IMPORT_DECISION_BOARD_REPORT.md) | **M1+M2+M3** 预检决策与评审委员会 |
| [../novel-suite/trial-import-decision-record/README.md](../novel-suite/trial-import-decision-record/README.md) | M1 试用预检决策记录 |
| [../novel-suite/freeze-import-decision-record/README.md](../novel-suite/freeze-import-decision-record/README.md) | M2 冻结预检决策记录 |
| [../novel-suite/legal-import-decision-board/README.md](../novel-suite/legal-import-decision-board/README.md) | M3 法律预检评审委员会 |
| [NOVEL_SUITE_N1N2N3_DECISION_FILL_KIT_REPORT.md](./NOVEL_SUITE_N1N2N3_DECISION_FILL_KIT_REPORT.md) | **N1+N2+N3** 人工填报与评审执行 |
| [../novel-suite/trial-decision-fill-kit/README.md](../novel-suite/trial-decision-fill-kit/README.md) | N1 试用决策填报包 |
| [../novel-suite/freeze-decision-fill-kit/README.md](../novel-suite/freeze-decision-fill-kit/README.md) | N2 冻结决策填报包 |
| [../novel-suite/legal-board-execution-kit/README.md](../novel-suite/legal-board-execution-kit/README.md) | N3 法律评审委员会执行 |
| [../novel-suite/video-production/handoff/README.md](../novel-suite/video-production/handoff/README.md) | Handoff 规格入口 |
| [../COMMERCIAL_RELEASE_GATE.md](../COMMERCIAL_RELEASE_GATE.md) | 商业发布前门禁清单（待法律复核） |
| [../THIRD_PARTY_POLICY.md](../THIRD_PARTY_POLICY.md) | 第三方与高风险依赖策略 |
| [../THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) | 第三方组件署名与许可 |

## Agent 入口

| 文档 | 说明 |
| --- | --- |
| [../AGENTS.md](../AGENTS.md) | **对话主路径**：`novel-pipeline` 一句话入口、Phase 0、多 IDE |
| [../novel-suite/rules-packs/](../novel-suite/rules-packs/) | 多 IDE 薄适配规则（Cursor/Codex/TRAE/Qoder/OpenClaw） |
| [verification/solo-2.0-命令状态.md](./verification/solo-2.0-命令状态.md) | **SOLO 三条复制块**（不读长文） |
| [standards/STRUCTURE-STANDARDS.md §1.4](./standards/STRUCTURE-STANDARDS.md) | Novel Suite 根契约（`.novel-suite-root`） |
| `novel suite doctor` | 工作区 / Skills / 引擎自检 |

## 规范与计划

| 文档 | 说明 |
| --- | --- |
| [standards/STRUCTURE-STANDARDS.md](./standards/STRUCTURE-STANDARDS.md) | 目录架构与文档存放规范 |
| [standards/PLATFORM-LENGTH-AND-NORMS.md](./standards/PLATFORM-LENGTH-AND-NORMS.md) | 各平台篇幅/章节与写作规范索引 |
| [standards/DECISION-PRINCIPLE.md](./standards/DECISION-PRINCIPLE.md) | 决策呈现原则（Agent 推荐、用户确认） |
| [standards/SKILLS-INSTALL.md](./standards/SKILLS-INSTALL.md) | Skill 清单与 Phase 0 对照 |
| [standards/POST-CODE-VERIFICATION.md](./standards/POST-CODE-VERIFICATION.md) | 代码交付前 Problems/linter 检查（强制） |
| [standards/SESSION-ARCHIVE.md](./standards/SESSION-ARCHIVE.md) | 压缩前归档（工作区 `docs/audit/session-archives/`） |
| [standards/NODE-EXECUTION-CONTRACT.md](./standards/NODE-EXECUTION-CONTRACT.md) | 节点执行契约（NEC）：分派表 + 完成清单 |
| [standards/DIRECTORY-ARCHITECTURE.md](./standards/DIRECTORY-ARCHITECTURE.md) | **目录架构 2.0** + 版本迭代规则 |
| [standards/layout-phase-map.json](./standards/layout-phase-map.json) | Phase→路径机器可读映射 |
| [standards/WORKSPACE-LAYOUT.md](./standards/WORKSPACE-LAYOUT.md) | 左侧目录速查 |
| [../novel-suite.code-workspace](../novel-suite.code-workspace) | 可选多根工作区视图 |
| [workflow/README.md](./workflow/README.md) | Phase 0–9 + 视频工作流导航 |
| [workflow/NEC-NODE-MAP.md](./workflow/NEC-NODE-MAP.md) | 节点传递方向、思维导图、NEC-11 §14 进度 |
| [standards/AUDIT-REFERENCES-INDEX.md](./standards/AUDIT-REFERENCES-INDEX.md) | Phase 0–9 / V0 审计脚本与语料索引 |
| [standards/PLATFORM-LENGTH-AND-NORMS.md](./standards/PLATFORM-LENGTH-AND-NORMS.md) | 各平台章均/日更/全勤字数口径（CJK vs 后台） |
| [plans/NEC-10-enrichment-matrix.md](./plans/NEC-10-enrichment-matrix.md) | 节点加厚成熟度矩阵 |
| [standards/GITHUB-RELEASE.md](./standards/GITHUB-RELEASE.md) | GitHub 创建仓库、上传与标准排版 |
| [plans/ROADMAP.md](./plans/ROADMAP.md) | 合并审计后的完善路线图 |
| [RELEASE-READINESS.md](./RELEASE-READINESS.md) | **发布就绪**：E2E 示例、清理脚本、验收表 |
| [RELEASE-NOTES-2.0.md](./RELEASE-NOTES-2.0.md) | **2.0.0** 版本说明（功能冻结） |
| [audit/2026-05-31-structure-compliance.md](./audit/2026-05-31-structure-compliance.md) | 第三层：目录与文档存放合规审计 |

## 子项目

| 项目 | README |
| --- | --- |
| 小说 | [../cursor-novel-writer/README.md](../cursor-novel-writer/README.md) |
| 视频 | [../cursor-novel-video/README.md](../cursor-novel-video/README.md) |

## 验证记录（部分完成）

| 平台 | 文档 |
| --- | --- |
| Cursor | [verification/cursor.md](./verification/cursor.md) |
| Qoder | [verification/qoder.md](./verification/qoder.md) |
| TRAE CN | [verification/trae-cn.md](./verification/trae-cn.md) |
| SOLO 克隆 | [verification/solo-clone-checklist.md](./verification/solo-clone-checklist.md) |
| SOLO NEC 测试对话 | [verification/solo-nec-dialogue.md](./verification/solo-nec-dialogue.md) |
| SOLO 选题→第一章 | [verification/solo-phase0-to-ch01-dialogue.md](./verification/solo-phase0-to-ch01-dialogue.md) |
| **SOLO 2.0 命令状态（复制粘贴）** | [verification/solo-2.0-命令状态.md](./verification/solo-2.0-命令状态.md) |
| **SOLO 2.0 测试命令（详解）** | [verification/solo-2.0-test-commands.md](./verification/solo-2.0-test-commands.md) |
| NEC 三端验收 | [verification/NEC-smoke-matrix.md](./verification/NEC-smoke-matrix.md) |
