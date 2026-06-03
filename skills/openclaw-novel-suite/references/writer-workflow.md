# Writer workflow (OpenClaw)

## New book

1. `novel-suite doctor --json`
2. `novel-suite writer scan --demo --period week --json` (or `--input hits.json` / live scan without `--demo`)
3. User picks concept from `details.themes` / concept artifacts → approve one brief
4. `novel-suite writer init --title ... --premise ... --concept intel/concepts/....md --json`
5. `novel-suite writer gate --phase 1 --project novels/<slug> --json` (often already `gate_phase_1: true` in init JSON)

## Next chapter

1. `novel-suite writer active --json`
2. `novel-suite writer gate --phase 5 --project novels/<slug> --json`
3. Read story, voice-brief, foreshadowing, characters (from project tree)
4. Agent writes draft to `/tmp/chNN.md` (+ optional snapshot markdown)
5. `novel-suite writer chapter draft`（`--project novels/<slug>`、`--chapter N`、`--input /tmp/chNN.md`、`--json`）
6. `novel-suite writer gate --phase 6 --project novels/<slug> --json` before review/export

## Review / export

- Review: `novel-review` skill or `reviews/chNN-review.md` with `## Blockers` and `(none)` if clean
- Gate: `novel-suite writer gate --phase 9 --project novels/<slug> --json`
- Export (JSON contract):

  ```bash
  novel-suite writer export --project novels/<slug> --format markdown --json
  novel-suite writer export --project novels/<slug> --format txt --json
  novel-suite writer export --project novels/<slug> --format epub --output dist/书名.epub --json
  ```

  `--json` stdout must be one JSON document (`json.loads` on full stdout).
  Legacy lines only in `details.legacy_output`.

  `--skip-gate` requires `NOVEL_SUITE_ALLOW_SKIP_GATE=1` (tests only).

Legacy `novel_cli.py export --format epub` unchanged for Cursor/Qoder/TRAE.
