---
name: plot-structure
description: |
  Plan arcs, chapter outlines, foreshadowing matrix. Supports three-act, 起承转合, save-the-cat.
  Use for 大纲、情节、伏笔、plot outline, 分章计划.
license: MIT
metadata:
  author: cursor-novel-writer
  version: "1.0.0"
---

# Plot Structure

## Node Execution Contract (NEC)

**执行前必读：** [references/node-dispatch.md](./references/node-dispatch.md)。完成后 `novel node sync --phase 3`。

Fuses story-skills plot frameworks + novel-skill foreshadowing matrix.

## Framework Selection

Ask or infer:

- **三幕式** (default for general CN fiction)
- **起承转合** (kishotenketsu)
- **Save the Cat** beats (optional)

Framework details: [references/plot-frameworks.md](./references/plot-frameworks.md)

## Deliverables

1. `plot/arcs/<arc-id>.md` — arc summary, stakes, climax
2. `plot/timeline.md` — ordered events
3. `plot/foreshadowing.md` — matrix:

| 元素 | 埋设章 | 发展 | 回收 | 状态 |
| --- | --- | --- | --- | --- || 旧照片 | Ch.2 | Ch.8 | Ch.15 | open |

4. `task_plan.md` — chapter checklist with titles and key beats
5. Update `chapters/_index.md` planned entries

## Chapter Outline Format (in task_plan.md)

```markdown
## 章节计划
- [ ] 第01章：标题 — 场景要点 (~4000字)
- [ ] 第02章：...
```

## After Outline

Suggest `chapter-writing` for draft, or `novel-review` for outline-only critique.
