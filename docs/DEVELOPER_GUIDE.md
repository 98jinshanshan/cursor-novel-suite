# Developer Guide — Novel Suite 2.0

## Install

```bash
pip install -e .
novel-suite version
novel-suite doctor --core-only --json
```

## Layout

```text
src/novel_suite/          # Installable package (Phase A–D core)
cursor-novel-writer/      # Legacy engine + IDE skills (unchanged entry)
cursor-novel-video/
skills/openclaw-novel-suite/  # OpenClaw orchestrator skill
tests/                    # Package + contract tests
```

## JSON Result Contract

See `src/novel_suite/core/result.py` and `skills/openclaw-novel-suite/references/result-contract.md`.

## Legacy compatibility

- `python cursor-novel-writer/engine/novel_cli.py` — unchanged subcommands
- `suite_paths.py` / `project_registry.py` — delegate to `novel_suite` when installed

## Project init (Phase H)

```bash
novel-suite writer init \
  --title "书名" \
  --premise "一句话梗概" \
  --concept intel/concepts/2026-W23-01-novel-xxx.md \
  --platform-target "晋江" \
  --json
```

`details.gate_phase_1` reports whether `writer gate --phase 1` passes immediately after init.

## Market scan (Phase F)

```bash
novel-suite writer scan --demo --period week --json
novel-suite writer scan --input intel/fixtures/smoke-hits.json --radar tmp/radar.md --json
```

JSON `details` includes `source_type`, `verified`, `sample_size`, `themes[]` with `confidence`.
Live web search still uses legacy DuckDuckGo path inside `intel_scan.py` (unverified).

## Chapter draft (Phase E)

```bash
novel-suite writer chapter draft \
  --project cursor-novel-writer/examples/demo-novel \
  --chapter 2 \
  --title "封存编号" \
  --input /tmp/ch02.md \
  --snapshot-input /tmp/ch02-snap.md \
  --json
```

Requires Phase 5 gate (`voice-brief` + prior phases). Existing chapters need `--force`.
`--skip-gate` only when `NOVEL_SUITE_ALLOW_SKIP_GATE=1` (tests/CI).

## Export (Phase I)

```bash
novel-suite writer export \
  --project cursor-novel-writer/examples/demo-novel \
  --format markdown \
  --json
```

Formats: `markdown`, `txt`, `epub`. Requires Phase 9 gate (or `--skip-gate` with `NOVEL_SUITE_ALLOW_SKIP_GATE=1`).
EPUB needs `ebooklib`; missing dependency returns `EPUB_DEPENDENCY_MISSING` (not fake success).
Legacy `novel_cli.py export --format epub` is unchanged.

## Video jobs (Phase G)

```bash
novel-suite video create-summary \
  --chapter 01_试章.md \
  --project cursor-novel-writer/examples/demo-novel \
  --json
novel-suite video run --job <job_id> --json
novel-suite video status --job <job_id> --json
```

`create-summary --run` runs the FFmpeg pipeline immediately (legacy one-shot).
`resume` retries pending/failed jobs. Legacy `video_cli.py` unchanged.

## Release readiness

发布前见 [RELEASE-READINESS.md](./RELEASE-READINESS.md) 与 OpenClaw
[smoke-checklist.md](../skills/openclaw-novel-suite/references/smoke-checklist.md)。

```powershell
powershell -File platforms/final-verify.ps1
```

## Tests

```bash
pytest tests/ -q
pytest -m "not ffmpeg" -q
```

## Roadmap (REFACTOR-PLAN)

| Phase | Status |
| --- | --- |
| A–D | `paths`, `doctor`, `registry`, `gate`, `novel-suite` CLI |
| E | `writer chapter draft` / `chapter promote` ✅ |
| F | `writer scan --demo/--input --json` ✅ (minimal; live search unchanged) |
| H | `writer init --json` ✅ (wraps `scaffold_project`) |
| I | `writer export --json` ✅ (markdown/txt/epub; Phase 9 gate) |
| G | `video create-summary` / `run` / `status` / `resume` --json ✅ |
| H+ | Full legacy shim to `novel-suite` |
