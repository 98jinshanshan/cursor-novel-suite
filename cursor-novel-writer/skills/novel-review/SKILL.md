---
name: novel-review
description: |
  Consistency review via graphify knowledge graph, editorial personas, and validation checklists.
  Use for 审稿、一致性检查、review chapter, 查伏笔, graphify, 润色前诊断.
license: MIT
compatibility: Requires graphify CLI for full graph features; full repo clone for scripts/. Offline checklists work without graphify.
metadata:
  author: cursor-novel-writer
  version: "1.0.0"
---

# Novel Review

Integrates graphify-novel, zencoder editor roles, postwriter validation layers.

## Hard Validators (must pass)

From postwriter-inspired checklist:

- [ ] POV 未漂移（对照 story.md）
- [ ] 时间线无矛盾（plot/timeline.md）
- [ ] 人物能力/位置与上一章一致
- [ ] 已回收伏笔在 foreshadowing.md 标记 resolved
- [ ] 无违反 worldbuilding/systems 规则

## Soft Critics (suggest fixes)

- [ ] 节奏：场景是否拖滞
- [ ] stakes：本章是否推动主线
- [ ] 对话：是否可删减说明性台词
- [ ] 主题：是否过度说教

## Graphify Commands

From project root (skill wrapper → engine):

```bash
python skills/novel-review/scripts/graphify_bridge.py --project . review --chapter chapters/03_*.md
python skills/novel-review/scripts/graphify_bridge.py --project . status
python skills/novel-review/scripts/graphify_bridge.py --project . query --from "陈薇" --to "林默"
python skills/novel-review/scripts/graphify_bridge.py --project . update --from-chapters
```

## Editorial Personas (zencoder-inspired)

| Persona | Focus | Output |
| --- | --- | --- |
| Ghostlight | 读者体验、困惑点 | 读者报告 |
| Lumen | 结构、节奏、弧光 | 修订清单 |
| Sable | 语法、一致性、用词 | 行级建议 |

Deep workflow: [references/forge-workflow.md](./references/forge-workflow.md)

Run one persona at a time; synthesize per Forge workflow.

## Output

Save review to `reviews/chNN-review.md` with severity: **blocker** / **warn** / **nit**.

Do not auto-rewrite full chapter unless user asks; provide surgical edits first.
