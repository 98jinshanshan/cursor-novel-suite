---
name: novel-suite
description: |
  Use when the user wants to create, plan, write, review, export Chinese novels,
  or turn novel chapters into short videos. Triggers: 写小说, 扫榜, 选题,
  开书, 续写, 写下一章, 审稿, 去AI味, 导出EPUB, 小说短视频, 章节视频.
---

# Novel Suite for OpenClaw

Use this skill when the user wants to write, plan, review, export Chinese novels,
or convert novel chapters into short videos.

**Do not** copy the 13 Cursor/TRAE atomic skills into OpenClaw. This skill is the
single orchestrator; it calls the unified `novel-suite` CLI.

## Required tooling

Prefer the installable CLI (Novel Suite 2.0):

```bash
novel-suite doctor --json
novel-suite writer gate --phase N --project novels/<slug> --json
```

Legacy entry points remain valid in the monorepo:

```bash
python cursor-novel-writer/engine/novel_cli.py suite doctor --core-only
python cursor-novel-writer/engine/novel_cli.py pipeline gate --phase 1 --project ...
```

## Execution principles

1. Run `novel-suite doctor --json` before writes.
2. Resolve `novel-suite writer active --json` or require explicit `--project`.
3. Phase 0 incomplete → do not draft chapters.
4. All CLI calls use `--json` when available; parse `status`, `code`, `message`, `next_actions`.
5. Agent generates prose; CLI handles registry, gate, and structured artifacts.
6. Never cross-write between `novels/<slug>` projects.
7. No external publish/upload without user confirmation.

## Core commands (writer)

| Intent | Command |
| --- | --- |
| Health | `novel-suite doctor --json` |
| Active book | `novel-suite writer active --json` |
| List books | `novel-suite writer list --json` |
| Switch book | `novel-suite writer use <slug> --json` |
| Phase gate | `novel-suite writer gate --phase <n> --project novels/<slug> --json` |
| Status | `novel-suite writer status --project novels/<slug> --json` |
| Chapter draft | `novel-suite writer chapter draft --project novels/<slug> --chapter N --title T --input draft.md --json` |
| Draft promote | `novel-suite writer chapter promote <file> --json` |

| Market scan | `novel-suite writer scan --demo --period week --json` |
| Init | `novel-suite writer init --title ... --premise ... --concept intel/concepts/x.md --json` |

Export: `novel-suite writer export --json`. Video: `novel-suite video *` — see
[writer-workflow.md](references/writer-workflow.md) and [video-workflow.md](references/video-workflow.md).

## Error handling

If `status` is `error`:

- Report `code` and `message` to the user.
- Offer `next_actions` as numbered steps.
- Do not advance to later phases while gate fails.

See [references/result-contract.md](references/result-contract.md).

## Workflows

- [writer-workflow.md](references/writer-workflow.md) — Phase 0–9
- [video-workflow.md](references/video-workflow.md) — summary video jobs
- [smoke-checklist.md](references/smoke-checklist.md) — **release smoke** (final-verify + JSON E2E)
- [safety.md](references/safety.md) — path and platform rules
- [troubleshooting.md](references/troubleshooting.md) — common failures
