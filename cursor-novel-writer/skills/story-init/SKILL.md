---
name: story-init
description: |
  Scaffold a new Chinese fiction project with story bible, folder structure, and registries.
  Use when starting a novel, creating story project, 新建小说, 开始写小说, init story, or novel init.
license: MIT
compatibility: Requires Python 3.10+ and full repo clone for scripts/. Optional graphify CLI.
metadata:
  author: cursor-novel-writer
  version: "1.1.0"
---

# Story Init

Initialize a Chinese general-fiction project. Fused from story-skills (structure) and novel-skill (Chinese workflow).

## Node Execution Contract (NEC)

**执行前必读：** [references/node-dispatch.md](./references/node-dispatch.md)。  
`novel init` 自动生成 `canon/nodes/phase-1.completion.json`（P1-S2 done）；gate phase 2 前完成 P1-S3。

## When to Use

- User wants to start a new novel from scratch
- User says: 新建小说、开始写故事、story init、创建项目
- **Prerequisite:** Phase 0 complete — `canon/concept-brief.md` exists (via `novel-market-scan` + `init --concept`)

## Steps

1. **Verify Phase 0 gate** (if not already done):

   ```bash
   python engine/novel_cli.py pipeline gate --phase 1 --project novels/<slug>
   ```

2. Gather via conversation (or CLI args if running `novel init`):
   - Title, genre, tone, target length (chapters × words)
   - POV (第一/第三人称), tense (过去/现在)
   - One-line premise

3. **Default path:** run CLI (creates `novels/<slug>/`, registers, sets active):

   ```bash
   python engine/novel_cli.py init --title "..." --premise "..." \
     --concept ../../intel/concepts/<slug>.md --platform-target 通用
   ```

   Use `--concept` when Phase 0 concept brief is ready in `intel/concepts/`.

4. Manual `--output` only when user explicitly needs a path outside `novels/`.

5. Project layout:

```text
novels/<slug>/
├── canon/concept-brief.md
├── canon/project.json
├── canon/progress.json
├── canon/voice-brief.md
├── canon/snapshots/
├── chapters/.drafts/
├── story.md
```

6. Copy templates from `templates/` in the repo (or use embedded defaults in references/).

7. Fill `story.md` with YAML frontmatter: title, genre, premise, pov, tense, themes.

8. Initialize `canon/progress.json` per `schema/progress.schema.json`.

9. **Graphify (required when CLI available):** run:

   ```bash
   python skills/story-init/scripts/graphify_bridge.py --project . init --premise "<premise>"
   ```

   If graphify is not installed, document in README and continue with markdown-only canon.

10. Update `task_plan.md` with Phase 1 complete; tell user next steps: worldbuilding → plot → **voice brief** → chapters.

For end-to-end orchestration, use skill **`novel-pipeline`**.

## Output Checklist

- [ ] `canon/concept-brief.md` present (Phase 0)
- [ ] `story.md` exists with complete frontmatter
- [ ] All `_index.md` registries created
- [ ] `canon/progress.json` initialized
- [ ] User knows trigger phrases for next skills

## References

- [Project structure](references/structure.md)
- [story.md template](references/story-template.md)
- [Phase 0 market scan](../novel-market-scan/SKILL.md)
