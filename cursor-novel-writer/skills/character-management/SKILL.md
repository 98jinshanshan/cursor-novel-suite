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
