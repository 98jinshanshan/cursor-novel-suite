# Novel Suite 工程实施计划

**版本：** 1.0（2026-06-10 执行包）  
**原则：** 先新增对齐层，不破坏旧结构；先文档/契约，后代码接入。

---

## 阶段 A — 本次已执行（文档与骨架）

| 步骤 | 产物 | 验收 |
| --- | --- | --- |
| A1 对齐报告 | `NOVEL_SUITE_ALIGNMENT_REPORT.md` | 结构/能力/缺口/风险齐全 |
| A2 实施计划 | 本文件 | 新增/不改/风险可追踪 |
| A3 产品边界 | `novel-suite/PRODUCT_BOUNDARY.md` | 自有核心/适配器/参考三层 |
| A4 第三方边界 | `novel-suite/THIRD_PARTY_BOUNDARY.md` | AGPL/GPL/平台禁入明确 |
| A5 Core contracts | `novel-suite/core/contracts/*.schema.md` | 4 份中立契约 |
| A6 Core gates | `novel-suite/core/gates/*.md` | DeAI/发布/来源风险 |
| A7 Core workflows | `novel-suite/core/workflows/*.md` | 4 条主流程 |
| A8 Prompt Packs | `novel-suite/prompt-packs/PP-*.md` | 3 Pack + README |
| A9 Rules Packs | `novel-suite/rules-packs/*/` | 6 IDE 薄适配 |
| A10 Adapters | `novel-suite/adapters/*/` | 4 类默认关闭 |
| A11 源映射 | `novel-suite/docs/AI_WORKSPACE_OS_SOURCE_MAP.md` | 文件→规格源可追溯 |
| A12 示例骨架 | `novel-suite/examples/demo_project_skeleton/` | 无真实章节正文 |
| A13 入口链接 | `README.md`, `docs/INDEX.md` | 非破坏性追加 |

**回滚：** 删除 `novel-suite/` 与两份根报告即可；不影响 `src/novel_suite` 与 legacy 引擎。

---

## 阶段 B — 工程接入（分批执行）

| 步骤 | 内容 | 状态 |
| --- | --- | --- |
| B1 | `novel-suite doctor --core-contracts`、JSON Schema、rules-packs 安装、合规三件套 | ✅ 见 `docs/NOVEL_SUITE_B1_EXECUTION_REPORT.md` |
| B2 | CLI/MCP 只读产品层：`product list/read/validate` | ✅ 见 `docs/NOVEL_SUITE_B2B3_EXECUTION_REPORT.md` |
| B3 | 虚构 demo `cold_case_echo` + 离线 E2E 测试 | ✅ 同上 |
| B4 | 商业发布前合规硬化：`ebooklib`→`epub` extra、README 降噪、`COMMERCIAL_RELEASE_GATE` | ✅ 见 `docs/NOVEL_SUITE_B4_EXECUTION_REPORT.md`（法律定稿仍待人工） |
| B5 | 真实用户样例包与销售页前置审查 | 待执行 |
| B6 | 多 IDE 试跑矩阵 + trial-cards + `.agent-rules` 仓内分发 | ✅ 见 `docs/NOVEL_SUITE_B6_EXECUTION_REPORT.md` |
| B7 | 商业发布候选包打包前最终门禁 | 待执行 |
| B8 | 对外交付候选包归档与版本标记 | 待执行 |

---

## 阶段 C — AI 短剧生产规格（文档层）

| 步骤 | 内容 | 状态 |
| --- | --- | --- |
| C1 | 五级生产契约（Scene/Shot/Keyframe/Generation/Timeline） | ✅ `novel-suite/video-production/contracts/` |
| C2 | 工作流、生产门禁、11 适配器默认关闭、quality 层、虚构样例 | ✅ 见 `docs/NOVEL_SUITE_C1C2_VIDEO_PRODUCTION_SPEC_REPORT.md` |
| C3 | 外部专业软件 handoff 文档包（OTIO/FCPXML/EDL/AI/NLE/VFX/FFmpeg 计划） | ✅ 见 `docs/NOVEL_SUITE_C3_HANDOFF_SPEC_REPORT.md` |
| C4 | video-production + handoff product layer 只读挂载 | ✅ 见 `docs/NOVEL_SUITE_C4_PRODUCT_LAYER_REPORT.md`（只读索引，不执行外部工具） |
| C5 | ComfyUI/OTIO/DaVinci adapter 原型（默认关闭 dry-run） | ✅ 见 `docs/NOVEL_SUITE_C5_ADAPTER_SKELETON_REPORT.md` |
| C6 | 短剧样例包商业前置审查 | ✅ 见 `docs/NOVEL_SUITE_C6C7_COMMERCIAL_PREFLIGHT_REPORT.md` |
| C7 | AI短剧生产销售页与交付包前置审查 | ✅ 同上 |
| C8 | 真实 Adapter 启用前安全评审规格 | ✅ 见 `docs/NOVEL_SUITE_C8C9_SECURITY_AND_RELEASE_GATE_REPORT.md` |
| C9 | 商业候选包打包清单与最终门禁 | ✅ 同上 |
| C10 | 多 IDE 用户试用脚本与反馈回收包 | ✅ 见 `docs/NOVEL_SUITE_F3_C10_TRACE_AND_TRIAL_REPORT.md` |
| C11 | 试用反馈复盘与产品包修订包 | ✅ 见 `docs/NOVEL_SUITE_F4F5_C11_BACKEND_AND_FEEDBACK_REPORT.md` |

---

## 阶段 F — Agent 架构显性化

| 步骤 | 内容 | 状态 |
| --- | --- | --- |
| F1 | Agent 架构文档包、框架 ADR、能力矩阵、权限/trace 模型 | ✅ 见 `docs/NOVEL_SUITE_F1_AGENT_ARCHITECTURE_REPORT.md` |
| F2 | Workflow Contract Schema 文档与样例包 | ✅ 见 `docs/NOVEL_SUITE_F2_WORKFLOW_CONTRACT_REPORT.md` |
| F3 | Trace/State 最小记录规格包 | ✅ 见 `docs/NOVEL_SUITE_F3_C10_TRACE_AND_TRIAL_REPORT.md` |
| F4 | LangGraph 可选 PoC 设计包（设计完成，非运行时） | ✅ 见 `docs/NOVEL_SUITE_F4F5_C11_BACKEND_AND_FEEDBACK_REPORT.md` |
| F5 | RAG/素材库后端候选研究包（研究完成，非运行时） | ✅ 同上 |

---

## 阶段 W — UI Agent Workbench MVP

| 步骤 | 内容 | 状态 |
| --- | --- | --- |
| W1 | `agent-entry-menu/` 6 项菜单 + validate/list CLI | ✅ 见 `docs/NOVEL_SUITE_W1W2_UI_AGENT_WORKBENCH_MVP_REPORT.md` |
| W2 | `src/novel_suite/server/` API + `ui-agent-workbench/` 静态 UI | ✅ 同上 |
| W2 | `server validate`（不长驻）/ `server run`（stdlib HTTP） | ✅ 同上 |

**商业发布仍 blocked** — UI 不直接写项目文件；market-scan 仅 demo。

---

## 阶段 G — 交付整理（非商业发布）

| 步骤 | 内容 | 状态 |
| --- | --- | --- |
| G1 | 产品交付总索引与冷启动上手包 | ✅ 见 `docs/NOVEL_SUITE_G1G2G3_DELIVERY_DEMO_LEGAL_REPORT.md` |
| G2 | 商业演示路线图与人工试用计划 | ✅ 同上 |
| G3 | 法律/权利/商业发布人工复核包 | ✅ 同上 |

**说明：** G 阶段完成交付/演示/复核**准备**；`commercial_release_allowed=false` 不变。

---

## 阶段 H — 人工试用、冻结候选、律师材料（非发布）

| 步骤 | 内容 | 状态 |
| --- | --- | --- |
| H1 | 人工试用执行包（本地反馈，无 telemetry） | ✅ 见 `docs/NOVEL_SUITE_H1H2H3_TRIAL_FREEZE_LEGAL_PACKET_REPORT.md` |
| H2 | 产品包冻结候选与版本命名（freeze_candidate_only） | ✅ 同上 |
| H3 | 律师/人工法律复核材料包（非法律意见） | ✅ 同上 |

---

## 阶段 I — 回填与对齐（非发布）

| 步骤 | 内容 | 状态 |
| --- | --- | --- |
| I1 | 人工试用记录回填包 | ✅ 见 `docs/NOVEL_SUITE_I1I2I3_INTAKE_ALIGNMENT_LEGAL_RESPONSE_REPORT.md` |
| I2 | 冻结候选版本对齐包（无 tag/zip/release） | ✅ 同上 |
| I3 | 法律/合规复核回填包（无自动关 blocker） | ✅ 同上 |

## 阶段 J — 人工会议与空白记录（非执行）

| 步骤 | 内容 | 状态 |
| --- | --- | --- |
| J1 | 首轮人工试用记录草案包（无伪造反馈） | ✅ 见 `docs/NOVEL_SUITE_J1J2J3_TRIAL_FREEZE_LEGAL_MEETING_REPORT.md` |
| J2 | 版本冻结评审会议包（无 tag/zip/release） | ✅ 同上 |
| J3 | 法律/合规评审会议包（无自动关 blocker） | ✅ 同上 |

## 阶段 K — 人工结果承接（非执行）

| 步骤 | 内容 | 状态 |
| --- | --- | --- |
| K1 | 人工试用结果承接包（无伪造反馈） | ✅ 见 `docs/NOVEL_SUITE_K1K2K3_RESULT_DECISION_RECORD_REPORT.md` |
| K2 | 版本冻结会议结果承接包（无 tag/zip/release） | ✅ 同上 |
| K3 | 法律/合规会议结果承接包（无自动关 blocker） | ✅ 同上 |

## 阶段 L — 导入预检（非导入）

| 步骤 | 内容 | 状态 |
| --- | --- | --- |
| L1 | 人工试用结果导入预检包（无真实导入） | ✅ 见 `docs/NOVEL_SUITE_L1L2L3_IMPORT_PREFLIGHT_REPORT.md` |
| L2 | 冻结会议结果导入预检包（无 tag/zip/release） | ✅ 同上 |
| L3 | 法律会议结果导入预检包（无自动关 blocker） | ✅ 同上 |

## 阶段 M — 预检决策与评审委员会（非导入）

| 步骤 | 内容 | 状态 |
| --- | --- | --- |
| M1 | 试用材料预检决策记录包（无真实导入） | ✅ 见 `docs/NOVEL_SUITE_M1M2M3_IMPORT_DECISION_BOARD_REPORT.md` |
| M2 | 冻结材料预检决策记录包（无 tag/zip/release） | ✅ 同上 |
| M3 | 法律材料预检决策与评审委员会包（不改 gate） | ✅ 同上 |

## 阶段 N — 人工填报与评审执行（非导入）

| 步骤 | 内容 | 状态 |
| --- | --- | --- |
| N1 | 试用材料决策填报包（无伪造反馈） | ✅ 见 `docs/NOVEL_SUITE_N1N2N3_DECISION_FILL_KIT_REPORT.md` |
| N2 | 冻结材料决策填报包（无 tag/zip/release） | ✅ 同上 |
| N3 | 法律评审委员会执行包（不改 gate） | ✅ 同上 |

---

## 不会修改的文件（阶段 A/B 默认）

- `G:\SOLO小说项目/**`
- `G:\Reasonix\SOLO小说视频项目/**`
- `src/novel_suite/**/*.py`（阶段 A 不动）
- `cursor-novel-writer/engine/**`（阶段 A 不动）
- `cursor-novel-video/engine/**`（阶段 A 不动）
- 用户数据 `novels/**` 正文

---

## 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 与现有 Skills 双轨 | Rules Pack 只指向 Core，不复制 Skill 正文 |
| 平行目录体系 | `novel-suite/` 为产品层；工程仍在 `src/novel_suite` |
| Prompt 与 Skill 漂移 | `AI_WORKSPACE_OS_SOURCE_MAP.md` 维护追溯 |
| 误启用第三方 | 所有 adapters 含 `ADAPTER_DISABLED_BY_DEFAULT.md` |

---

## 下一步建议（单选确认即可批量推进）

1. **工程接入包：** B1–B3 一次性 PR（改 CLI + install 脚本，仍不碰 SOLO/Reasonix）
2. **测试包：** B6 + 契约 JSON Schema 化（从 `.schema.md` 导出 `.json`）
3. **合规包：** B4 + B5 许可证与 NOTICES 落地
