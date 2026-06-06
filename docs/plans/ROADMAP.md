# 完善路线图（合并两层审计）

**来源：** [第一层审计](../audit/2026-05-31-novel-suite.md) + [交叉审计](../audit/2026-05-31-reference-crosswalk.md)  
**规范：** [STRUCTURE-STANDARDS.md](../standards/STRUCTURE-STANDARDS.md)

---

## P0 — 阻塞与规范基线

- [x] 文档目录重排（`docs/audit|standards|plans|verification/`）
- [x] 第三层结构合规审计
- [x] 决策呈现原则（`.cursor/rules` + `docs/standards/DECISION-PRINCIPLE.md`）
- [x] 修复 `create_epub.py`：`EpubNav` API
- [x] 修复 `graphify_bridge` / `novel_cli`：`--project` 参数（子命令前后均可 + subprocess 顺序）
- [x] 统一 CLI 文档
- [x] 清空并忽略 `tmp/video_jobs/`
- [x] graphify-novel upstream 命令表 →
  [graphify-upstream-verification.md](../cursor-novel-writer/docs/graphify-upstream-verification.md)
- [x] GitHub 创建仓库并首次 push → [GITHUB-RELEASE.md](../standards/GITHUB-RELEASE.md)（`98jinshanshan/cursor-novel-suite`）
- [x] `docs/verification/*.md` 多平台（Cursor/Qoder/TRAE 安装与仓内 smoke 已补；UI 手测模板已补）

**已确认决策（2026-05-31）：** Option A 脚本架构；demo-novel = 3 人物 + 2 地点 + 1 世界观 + 1 弧 + 1 章

## P1 — 参考项目补全（高 ROI）

- [x] `examples/demo-novel` 对标 story-skills the-last-ember（3人2地1规则1弧1章）
- [x] Skill `scripts/` 与 `engine/scripts/` 对齐（Option A wrapper）
- [x] `novel-review/references/forge-workflow.md`
- [x] `plot-structure/references/plot-frameworks.md`
- [x] beat-lock + 基础字幕（`beat_lock.py` / `burn_subtitles.py`，CLI `--subtitles`）
- [x] `cursor-novel-video/demos/` 样片文件（`demo-novel-ch01-summary-9x16-subtitled.mp4`）
- [x] `adapters/README.md`
- [x] `cursor-novel-writer/docs/graphify-upstream-commands.md`（草案）
- [x] `docs/verification/*.md` 多平台安装实测（Cursor/Qoder/TRAE 仓内 smoke 已完成）

**状态：** P1 主体已完成（2026-05-31）。剩余：Qoder/TRAE 实测。

## P2 — 选择性增强

- [x] knowledge-video 式逐段合成 → drama 增强（per-scene TTS + synced Ken Burns）
- [x] mcp-video 字幕工具子集（generate_subtitles / burn_subtitles / render_drama）
- [x] Novel Master 营销 skill（`novel-marketing`）
- [x] Claude marketplace 插件桩（`.claude-plugin/`）
- [x] pytest smoke + CI markdownlint（`.github/workflows/ci.yml`）

**状态：** P2 已完成（2026-05-31）。可选后续：Qoder/TRAE 实测。

## P3 — Workflow 编排与验证闭环（2026-06-01）

- [x] 第三层合成分析 → [workflow-validation-synthesis.md](../audit/2026-06-01-workflow-validation-synthesis.md)
- [x] `novel-pipeline` 总控 Skill（delegate 现有 9 原子 Skill）
- [x] `novel-review` v1.1：deai-checklist、personas、Forge 4–5 阶段
- [x] `templates/voice-brief.md` + demo-novel 示例
- [x] `novel_cli.py pipeline status`

**状态：** P3 已完成。安装：`npx skills add ./cursor-novel-writer -a cursor -y` 或补 junction 至 `novel-pipeline`。

## P4 — 多书隔离与平台合规（2026-06-02）

- [x] 第四层差距矩阵 → [full-reference-gap-matrix.md](../audit/2026-06-02-full-reference-gap-matrix.md)
- [x] `novels/` + `_registry.json` + `.active` + `canon/project.json`
- [x] `engine/scripts/project_registry.py` + CLI `init/list/use/active/promote`
- [x] 产物路由：`.drafts/`、`canon/snapshots/`、`reviews/`
- [x] `platform-compliance.md` + deai 平台节 + voice-brief platform_target
- [x] novel-pipeline / story-init / chapter-writing / novel-review v1.1 隔离规则
- [x] `.gitignore` novels 用户内容

**状态：** P4 已完成。P5 见下。

## P5 — 参考补全（高 ROI，2026-06-02）

- [x] NS-11 / VS-10 Quick trigger 一览表
- [x] GN-06 `novel_cli graphify query`
- [x] PW-04 soft-critics.md（10 条）
- [x] PW-07 review-repair-spec 模板
- [x] NM-05 `novel_cli bible summary`
- [x] ZE-08 Quill export audit checklist
- [x] SVM-06 RESULT JSON 契约（video engine scripts）
- [x] SVM-09 video-chapter-summary/references/PIPELINE.md
- [x] SS-05 双向关系 reference + `novel relations check`

**状态：** P5 已完成（2026-06-02）。P6 暂缓（用户确认）。

## P-1 — 市场情报与选品层（2026-06-02，路径 C）

- [x] Skill `novel-market-scan` + `novel intel scan`（扫榜 + 短视频评分）
- [x] `intel/radar/` + `intel/concepts/` + monorepo README
- [x] `templates/concept-brief.md` + rubric / platform-scan / radar 模板
- [x] `novel-pipeline` Phase 0 gate + `novel pipeline gate` / `novel intel paths`
- [x] `novel init --concept` → `canon/concept-brief.md`
- [ ] P-1e 远期：`novel-publish` 平台上传（webnovel-writer 借鉴）

**状态：** P-1a–d 已完成（V1 Agent 搜索版）。

## P6 — SOLO 专家团架构升级（2026-06-07）

> 计划全文：[SOLO-ARCHITECTURE-UPGRADE.md](./SOLO-ARCHITECTURE-UPGRADE.md)  
> 协作规则：`.cursor/rules/ficus-incremental-delivery.mdc`

- [x] SOLO 文档审计 + 架构升级计划
- [x] FICUS 增量交付 Cursor 规则
- [x] Sprint 1.1：`novel-suite memory` 四层文件存储 + 双轨 recall + CLI
- [x] Sprint 1.2：Qdrant 后端 + `memory probe/sync` + install-memory-stack.ps1
- [x] Sprint 0：文档 D P0（pre-commit、docker-compose 127.0.0.1、sanitizer、subprocess_safe）
- [ ] Sprint 2：Wan T2V 全量 ref + Brain QC 自动 REPAIR E2E
- [ ] Sprint 3：Playwright 多平台发布
- [ ] Sprint 4–5：一致性自动化 + 数据飞轮

**状态：** P6 已启动（Sprint 1.1 落地）。

## R0–R5 — 可移植根契约与安装（2026-06-01 迭代）

- [x] **R0** `.novel-suite-root` + `suite_paths.py`（`NOVEL_SUITE_ROOT` / 向上遍历）
- [x] **R1** 文档去硬编码路径 → `<NOVEL_SUITE_ROOT>` / 结构契约（§1.4）
- [x] **R2** `novel suite doctor` + `suite_doctor.py`
- [x] **R3** `platforms/install-skills.ps1` 自动定位套件根
- [x] **R4** Skills 安装 junction 优先（`-Copy` 回退）
- [x] **R5** TRAE SOLO `solo-agent-prompt.md` + verification 排障链

**状态：** R0–R5 已完成。后续：各 IDE UI 手测补录。

## X-07 — Schema 门控（2026-06-01）

- [x] `schema/project.schema.json` + `registry.schema.json` + `progress.schema.json`
- [x] `engine/scripts/pipeline_gate.py` — JSON schema + 阶段产物校验
- [x] `novel pipeline gate` / `novel pipeline validate`
- [x] pytest：`gate --phase 6` 拦截、坏 project.json 拦截、`validate` OK

**状态：** X-07 已完成。

## X-08 — 视频 job ↔ 小说绑定（2026-06-01）

- [x] `cursor-novel-video/engine/scripts/novel_bind.py`
- [x] `storyboard.json` / `job_state.json` 写入 `novel` 元数据
- [x] `novels/_registry.json` 条目 `video_jobs[]` 自动登记/更新
- [x] `video_cli summary|drama --project novels/<slug> --chapter ...`
- [x] pytest：binding + registry 登记

**状态：** X-08 已完成。

## P6 — NEC 节点执行契约（2026-06-02）

- [x] [NODE-EXECUTION-CONTRACT.md](../standards/NODE-EXECUTION-CONTRACT.md)
- [x] `schema/node-completion.schema.json` + `engine/scripts/node_completion.py`
- [x] Phase 0 样板：`novel-market-scan` 分派表 + `intel scan` 写 `*.completion.json`
- [x] Phase 1–9 + 视频 V0–V2：`references/node-dispatch.md` v1
- [x] `novel node validate` · gate phase 1 校验 project phase-0 manifest
- [x] 目录导航：`docs/workflow/README.md` · `skills/README.md`

**状态：** P6 NEC-0/1 + 分派表 v1 已完成。

**批量执行：** [NEC-10-batch-execution.md](./NEC-10-batch-execution.md)（**NEC-10 全部批次 A–E ✅** 2026-06-03）。

## P8 — 十二参考主动跟踪（2026-06-01，P1 还债）

**矩阵源：** [full-reference-gap-matrix.md](../audit/2026-06-02-full-reference-gap-matrix.md)  
**每月 diff：** `novel suite gap-diff` → `docs/audit/gap-matrix-snapshots/YYYY-MM.json` + `gap-matrix-diff-YYYY-MM.md`

### 开放 backlog（勾选 = 矩阵 §4.3 + 仍 ⚠️/❌ 项）

| ID | 主题 | 优先级 | 状态 |
| --- | --- | --- | --- |
| X-06 | graphify thread 管理（GN-08） | 建议 | [ ] |
| GN-02 | graphify init --from-chapters | 可选 P5 | [ ] |
| GN-05 | graphify update --manual/--lore | 可选 P5 | [ ] |
| GN-11 | 独立 graphify companion skill | 可选 | [ ] |
| NS-03 | task_plan Characters 摘要表 | 可选 | [ ] |
| NS-04 | 伏笔矩阵列名 upstream 兼容 | 可选 | [ ] |
| SS-04 | kebab-case ID schema 校验 | 可选 | [ ] |
| SS-12 | worldbuilding references 模板 | 建议 | [ ] |
| SS-14 | Copilot 安装路径文档 | 可选 | [ ] |
| SS-11 | Claude marketplace 完善 | 可选 | [ ] |
| VS-01 | tumblr-video skill | 可选 P6 | [ ] |
| VS-02 | knowledge-video 完整（summary 增强） | 可选 | [ ] |
| SVM-04/11 | Whisper + loudnorm | 可选 | [ ] |
| FW-03 | Ghostlight pacing 脚本问题 | 建议 | [ ] |
| NM-01 | story-init requirements-table | 建议 P5 | [ ] |
| NM-02 | voice-brief 可配置章字数 | 可选 | [ ] |

**维护规则：** 关闭项在矩阵 §2 把「P3 后」改为 ✅，再跑 `suite gap-diff`；ROADMAP 行改 `[x]`。

## P7 — 目录架构 2.0（2026-06-03）

- [x] [DIRECTORY-ARCHITECTURE.md](../standards/DIRECTORY-ARCHITECTURE.md) + [layout-phase-map.json](../standards/layout-phase-map.json)
- [x] `.novel-suite-root` 增加 `layout-version` / `nec-version`
- [x] `suite doctor` → `layout_version` 检查
- [x] `novel-suite.code-workspace` 多根视图；隐藏 `.agents/.qoder/.trae`
- [x] 批次 B：`novel node sync` phase 1–3 + demo `canon/nodes/phase-*.completion.json`
- [x] 批次 C–E：phase 4–9 sync、video `node.completion.json`、NEC-smoke-matrix
