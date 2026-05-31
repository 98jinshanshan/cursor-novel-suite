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
- [x] graphify-novel upstream 命令表 1:1 对照 → [graphify-upstream-verification.md](../cursor-novel-writer/docs/graphify-upstream-verification.md)（graphifyy CLI + bridge 重写，2026-05-31）
- [x] GitHub 创建仓库并首次 push → [GITHUB-RELEASE.md](../standards/GITHUB-RELEASE.md)（`98jinshanshan/cursor-novel-suite`）
- [ ] `docs/verification/*.md` 多平台（Cursor 部分完成；Qoder/TRAE 预留）

**已确认决策（2026-05-31）：** Option A 脚本架构；demo-novel = 3 人物 + 2 地点 + 1 世界观 + 1 弧 + 1 章

## P1 — 参考项目补全（高 ROI）

- [x] `examples/demo-novel` 对标 story-skills the-last-ember（3人2地1规则1弧1章）
- [x] Skill `scripts/` 与 `engine/scripts/` 对齐（Option A wrapper）
- [x] `novel-review/references/forge-workflow.md`
- [x] `plot-structure/references/plot-frameworks.md`
- [x] beat-lock + 基础字幕（`beat_lock.py` / `burn_subtitles.py`，CLI `--subtitles`）
- [x] `cursor-novel-video/demos/` 样片（demo-novel 第1章 summary）
- [x] `adapters/README.md`
- [x] `cursor-novel-writer/docs/graphify-upstream-commands.md`（草案）
- [ ] `docs/verification/*.md` 多平台安装实测（Cursor 部分完成）

**状态：** P1 主体已完成（2026-05-31）。剩余：Qoder/TRAE 实测。

## P2 — 选择性增强

- [x] knowledge-video 式逐段合成 → drama 增强（per-scene TTS + synced Ken Burns）
- [x] mcp-video 字幕工具子集（generate_subtitles / burn_subtitles / render_drama）
- [x] Novel Master 营销 skill（`novel-marketing`）
- [x] Claude marketplace 插件桩（`.claude-plugin/`）
- [x] pytest smoke + CI markdownlint（`.github/workflows/ci.yml`）

**状态：** P2 已完成（2026-05-31）。可选后续：Qoder/TRAE 实测。
