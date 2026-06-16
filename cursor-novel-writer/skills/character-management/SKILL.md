---
name: character-management
description: |
  Create and maintain character profiles with relationships, arcs, and registry updates.
  Use for 创建人物、角色设定、character profile, add character, 人物关系.
license: MIT
metadata:
  author: cursor-novel-writer
  version: "1.0.0"
---

# Character Management

## Node Execution Contract (NEC)

**执行前必读：** [references/node-dispatch.md](./references/node-dispatch.md)。  
与 worldbuilding 同属 Phase 2；完成后 `novel node sync --phase 2`。

From story-skills: rich profiles + bidirectional relationship links.

## Steps

1. Read `story.md` and `characters/_index.md`.
2. For new character, assign kebab-case `id` (e.g. `chen-wei`).
3. Create `characters/<id>.md` with frontmatter (example):

   ```yaml
   ---
   id: chen-wei
   name: 陈薇
   role: protagonist
   traits: [冷静, 固执]
   arc: 从旁观者到决策者
   relationships:
     - target: lin-mo
       type: 同事/秘密同盟
   ---
   ```

4. Update `characters/_index.md` table.
5. Update related characters' `relationships` (bidirectional). See
   [references/bidirectional-relations.md](./references/bidirectional-relations.md).
6. After major chapter events, run graphify update:

   ```bash
   python skills/character-management/scripts/graphify_bridge.py --project . update --from-chapters
   ```

## Writing Checklist

- [ ] Voice notes (说话习惯、口头禅)
- [ ] Goals / fears / secrets
- [ ] Arc beats tied to plot arcs

## Sprint 7 新增

- `novel_suite.writer.character_gen.extract_character(text, name)` 从正文自动提取角色设定卡
- `novel-suite video character qc` 可验证角色一致性（与 gate consistency 联动）
- `generate_cvdp_from_chapters(project)` 批量准备 CVDP 角色素材任务
