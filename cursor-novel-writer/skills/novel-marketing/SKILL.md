---
name: novel-marketing
description: |
  Generate marketing copy from story bible: blurb, tagline, social hooks. Optional; user-request only.
  Use for 书籍简介、宣传文案、blurb、营销、新书预告.
license: MIT
compatibility: Markdown-only; no scripts required. Reads story.md and canon files.
metadata:
  author: cursor-novel-writer
  version: "1.0.0"
---

# Novel Marketing

## Node Execution Contract (NEC)

**管线外可选节点** — 不绑定 Phase 0–9，无 `canon/nodes/phase-*.completion.json`。  
用户明确要求营销文案时再启用；导出后可 delegate 本 Skill（见 `novel-export` Chat Summary）。

From Novel Master: turn `story.md` + arc into platform-ready copy. **Only when user asks.**

## Inputs

- `story.md` (title, genre, premise, themes)
- `plot/arcs/*.md` (stakes, hook)
- Optional: sample chapter for tone

## Outputs (pick what user needs)

1. **Blurb** 150–250 字（悬疑/类型小说）
2. **Tagline** ≤ 20 字
3. **Social hooks** 3 条（小红书 / 微博风格，无剧透或可控剧透）

Templates: [references/blurb-templates.md](./references/blurb-templates.md)

## Rules

- Do not invent plot beats not in canon
- Match genre and tone from story.md
- Export to `dist/marketing.md` if user wants a file
