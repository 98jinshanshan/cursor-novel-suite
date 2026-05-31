---
name: story-init
description: |
  Scaffold a new Chinese fiction project with story bible, folder structure, and registries.
  Use when starting a novel, creating story project, 新建小说, 开始写小说, init story, or novel init.
license: MIT
compatibility: Requires Python 3.10+ and full repo clone for scripts/. Optional graphify CLI.
metadata:
  author: cursor-novel-writer
  version: "1.0.0"
---

# Story Init

Initialize a Chinese general-fiction project. Fused from story-skills (structure) and novel-skill (Chinese workflow).

## When to Use

- User wants to start a new novel from scratch
- User says: 新建小说、开始写故事、story init、创建项目

## Steps

1. Gather via conversation (or CLI args if running `novel init`):
   - Title, genre, tone, target length (chapters × words)
   - POV (第一/第三人称), tense (过去/现在)
   - One-line premise

2. Create project layout under current directory or `--output`:

```text
<project>/
├── story.md
├── task_plan.md
├── canon/progress.json
├── characters/_index.md
├── worldbuilding/_index.md
├── worldbuilding/locations/
├── worldbuilding/systems/
├── plot/_index.md
├── plot/arcs/
├── plot/timeline.md
├── plot/foreshadowing.md
├── chapters/_index.md
└── graphify-out/          # graphify knowledge graph output
```

3. Copy templates from `templates/` in the repo (or use embedded defaults in references/).

4. Fill `story.md` with YAML frontmatter: title, genre, premise, pov, tense, themes.

5. Initialize `canon/progress.json` per `schema/progress.schema.json`.

6. **Graphify (required when CLI available):** run:

   ```bash
   python skills/story-init/scripts/graphify_bridge.py --project . init --premise "<premise>"
   ```

   If graphify is not installed, document in README and continue with markdown-only canon.

7. Update `task_plan.md` with Phase 1 complete; tell user next steps: worldbuilding → plot → chapters.

## Output Checklist

- [ ] `story.md` exists with complete frontmatter
- [ ] All `_index.md` registries created
- [ ] `canon/progress.json` initialized
- [ ] User knows trigger phrases for next skills

## References

- [Project structure](references/structure.md)
- [story.md template](references/story-template.md)
