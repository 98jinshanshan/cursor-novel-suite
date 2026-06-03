# Safety

## Writes

- Only under `novels/<slug>/` or explicit `--project` paths inside `novels/` or `examples/`.
- Normalize paths; reject traversal outside project root.

## Market scan

- Label sources as unverified unless `verified: true` in intel metadata.
- Do not claim results are official platform hot lists.

## Content

- No auto-publish to platforms.
- Export only after gates pass and no open review blockers.

## Video

- Long renders use job + status; do not block the agent with blind sleep loops.
