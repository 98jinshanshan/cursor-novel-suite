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
