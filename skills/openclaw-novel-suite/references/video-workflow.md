# Video workflow (OpenClaw)

## Agent flow (Phase G)

```bash
novel-suite video create-summary --chapter 01_试章.md \
  --project cursor-novel-writer/examples/demo-novel --json
novel-suite video run --job <job_id> --json
novel-suite video status --job <job_id> --json
```

On failure: `novel-suite video resume --job <job_id> --json`

One-shot (legacy-style): add `--run` to `create-summary` (requires FFmpeg).

Jobs live under `cursor-novel-video/tmp/video_jobs/<job_id>/` with `job_state.json`.

`--json` stdout is a single JSON document (`json.loads` on full stdout).

## Legacy CLI (unchanged)

```bash
python cursor-novel-video/engine/video_cli.py summary --chapter ... --project ...
```
