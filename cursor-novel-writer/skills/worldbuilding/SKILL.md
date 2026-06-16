---
name: worldbuilding
description: |
  Build locations, world systems (rules, politics, technology). Use for 世界观、设定、地点、魔法体系、背景设定.
license: MIT
metadata:
  author: cursor-novel-writer
  version: "1.0.0"
---

# Worldbuilding

## Node Execution Contract (NEC)

**执行前必读：** [references/node-dispatch.md](./references/node-dispatch.md)。完成 Phase 2a 后运行 `novel node sync --phase 2`。

## Steps

1. Read `story.md`, `worldbuilding/_index.md`.
2. Create location: `worldbuilding/locations/<id>.md`
3. Create system: `worldbuilding/systems/<id>.md` (rules that must not break)
4. Register in `_index.md`.
5. Link characters to locations where relevant.

## System File Template

```yaml
---
id: city-governance
name: 城政规则
category: politics
rules:
  - 夜间宵禁 22:00
  - 外来者需登记
---
```

## Consistency

Any rule in `systems/` is **hard canon**. Chapter-writing must not violate without
explicit retcon in `plot/timeline.md`.

## 关联模块

- `novel-suite video character pack` 中的 `appearance_class` 和 `consistency_token` 应与世界观设定一致
- 平台注册表（`platforms/_registry.py`）中的 `chapter_word_limit` 可对照世界观节奏规划
