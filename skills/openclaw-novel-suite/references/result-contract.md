# JSON Result Contract

All `novel-suite` commands support `--json` and emit:

```json
{
  "status": "ok",
  "code": "GATE_OK",
  "message": "Phase gate passed (enter phase>=1)",
  "artifacts": [{ "type": "file", "path": "cursor-novel-writer/examples/demo-novel" }],
  "next_actions": []
}
```

On failure:

```json
{
  "status": "error",
  "code": "PHASE0_NOT_COMPLETE",
  "message": "Phase gate failed for phase>=5",
  "required": ["task_plan.md: Phase 4 not marked [x]"],
  "next_actions": ["Complete prior phases in task_plan.md before entering phase 5"]
}
```

## Gate error codes

| Code | Meaning |
| --- | --- |
| `PHASE0_NOT_COMPLETE` | Concept / Phase 0 not done |
| `TASK_PLAN_PHASE_NOT_MARKED` | Prior phase not `[x]` in task_plan |
| `MISSING_CONCEPT_BRIEF` | canon/concept-brief.md incomplete |
| `MISSING_PROJECT_JSON` | project.json schema/artifact |
| `MISSING_PROGRESS_JSON` | progress.json |
| `MISSING_CHARACTER_PROFILES` | Phase 2 characters |
| `MISSING_WORLDBUILDING` | Locations/systems |
| `MISSING_CHAPTER` | No chapter files |
| `OPEN_REVIEW_BLOCKERS` | Review has open blockers |
| `GATE_FAIL` | Other gate failure |
| `CHAPTER_ALREADY_EXISTS` | Chapter file exists (use `--force`) |
| `SNAPSHOT_INPUT_NOT_FOUND` | `--snapshot-input` path missing |
| `INVALID_CHAPTER_NUMBER` | `--chapter` not in 1..999 |
| `SKIP_GATE_NOT_ALLOWED` | `--skip-gate` without env allow flag |
| `SCAN_OK` | Phase 0 radar + concepts written |
| `SCAN_NO_HITS` | No hits from demo/input/live |
| `DEMO_FIXTURE_MISSING` | `intel/fixtures/smoke-hits.json` absent |
| `SCAN_INPUT_NOT_FOUND` | `--input` path missing |
| `SCAN_INVALID_PLATFORMS` | Invalid `--platforms` list |
| `INIT_OK` | Novel project scaffolded |
| `CONCEPT_NOT_FOUND` | `--concept` path missing |
| `INIT_TITLE_REQUIRED` | Empty `--title` |
| `INIT_PREMISE_REQUIRED` | Empty `--premise` |
| `EXPORT_OK` | Manuscript written to dist/ or `--output` |
| `EXPORT_BLOCKED` | Phase 9 gate not satisfied |
| `EXPORT_FAILED` | No chapters, IO error, or epub script failure |
| `INVALID_EXPORT_FORMAT` | `--format` not markdown/txt/epub |
| `EPUB_DEPENDENCY_MISSING` | `ebooklib` not installed |
| `GATE_PHASE9_BLOCKED` | Alias avoided — use `EXPORT_BLOCKED` |
| `VIDEO_CREATE_OK` | Job created (`status: pending`, `stage: intake`) |
| `VIDEO_STATUS_OK` | Job status read (pending/running/succeeded) |
| `VIDEO_STATUS_FAILED` | Job failed (see `details.stage`, `resume`) |
| `VIDEO_RUN_OK` / `VIDEO_RUN_FAILED` | Pipeline run finished |
| `VIDEO_JOB_NOT_FOUND` | Unknown `--job` id |
| `VIDEO_CHAPTER_NOT_FOUND` | Chapter path missing |
| `VIDEO_RESUME_BLOCKED` | Already succeeded or still running |

## Parsing rules

1. Prefer JSON over stderr text.
2. Never claim success when `status` is `error`.
3. Surface `next_actions` before asking open-ended questions.
