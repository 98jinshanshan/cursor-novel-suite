---
name: novel-review
description: |
  Consistency review via graphify, editorial personas (Ghostlight/Lumen/Sable), de-AI checklist, and validate-then-rewrite gates.
  Use for 审稿、一致性检查、review chapter, 查伏笔, graphify, 润色前诊断, 去AI味, de-AI.
license: MIT
compatibility: Requires graphify CLI for full graph features; full repo clone for scripts/. Offline checklists work without graphify.
metadata:
  author: cursor-novel-writer
  version: "1.1.0"
---

# Novel Review

## Node Execution Contract (NEC)

**执行前必读：** [references/node-dispatch.md](./references/node-dispatch.md)。  
Phase 6→8 分别 `novel node sync --phase 6|7|8`；报告须含 `## Blockers`、`## De-AI`、`Re-validate`。

Integrates graphify-novel, zencoder editor roles, postwriter validation layers, de-AI pass.

## Hard Validators (must pass)

**章节格式（Blocker）：** 对照 [../chapter-writing/references/chapter-format.md](../chapter-writing/references/chapter-format.md)

- [ ] `# 第N章：标题` 与文件名一致
- [ ] 默认 `continuous`：**不得**有章内 `## 一/二/三` 或单独一行「一」「二」「三」
- [ ] 须有 `# 第N章`、`---`、`（第N章完）`（见 chapter-format.md）
- [ ] 仅当 `voice-brief` 显式 `scene-beats` 时才允许三节拍小节

From postwriter-inspired checklist:

- [ ] POV 未漂移（对照 story.md）
- [ ] 时间线无矛盾（plot/timeline.md）
- [ ] 人物能力/位置与上一章一致
- [ ] 已回收伏笔在 foreshadowing.md 标记 resolved
- [ ] 无违反 worldbuilding/systems 规则

## Soft Critics (suggest fixes)

Full 10-item list: [references/soft-critics.md](./references/soft-critics.md)

- [ ] 节奏 / stakes / 对话 / 主题 / 文风（见 soft-critics §1–5）
- [ ] 场景感 / 悬念 / 动机 / 副线 / 信息密度（§6–10）

## De-AI Pass（Phase 7）

Full checklist: [references/deai-checklist.md](./references/deai-checklist.md)  
Persona: [references/personas/sable.md](./references/personas/sable.md)

**Gate:** 任一 deai ❌ → 不得 export；fix → re-review（forge 阶段 5，最多 2 轮）。

## Graphify Commands

From project root (skill wrapper → engine):

```bash
python skills/novel-review/scripts/graphify_bridge.py --project . review --chapter chapters/03_*.md
python skills/novel-review/scripts/graphify_bridge.py --project . status
python skills/novel-review/scripts/graphify_bridge.py --project . query --from "陈薇" --to "林默"
python engine/novel_cli.py graphify query --character "陈薇" --project novels/<slug>
python skills/novel-review/scripts/graphify_bridge.py --project . update --from-chapters
```

> `review` 在无 graphify 可用时会返回非零状态，避免“离线假通过”。

## Editorial Personas (zencoder-inspired)

| Persona | Focus | Prompt file |
| --- | --- | --- |
| Ghostlight | 读者体验、困惑点 | [personas/ghostlight.md](./references/personas/ghostlight.md) |
| Lumen | 结构、节奏、弧光 | [personas/lumen.md](./references/personas/lumen.md) |
| Sable | 去 AI 味、行编辑 | [personas/sable.md](./references/personas/sable.md) |

Deep workflow: [references/forge-workflow.md](./references/forge-workflow.md)（含阶段 4–5 de-AI + re-validate）

Run one persona at a time; synthesize per Forge workflow.

## Project isolation（P4）

- Reports only in `<project>/reviews/` — resolve via `novel active` or `--project novels/<slug>`
- Read `canon/project.json` → `platform_target`; check [platform-compliance.md](./references/platform-compliance.md)
- Revisions: `chapters/.drafts/` → `novel promote` after pass

## Review Report Template

Save to `reviews/chNN-review.md`:

```markdown
# Review — 第N章

## Blockers
- (none)

## Ghostlight
- ...

## Lumen
- ...

## Sable
- ...

## Platform
- [ ] platform_target 合规

## De-AI
- [ ] 项… ✅/❌

## Re-validate (round 1/2)
- ...

## Forge 修订计划
1. ...

Repair action spec table: [templates/review-repair-spec.md](../../templates/review-repair-spec.md)
```

Do not auto-rewrite full chapter unless user asks; provide surgical edits first.

For full pipeline orchestration use skill **`novel-pipeline`**.
