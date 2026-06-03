# Troubleshooting

| Symptom | Action |
| --- | --- |
| `SUITE_ROOT_NOT_FOUND` | Open monorepo root or set `NOVEL_SUITE_ROOT` |
| `NO_ACTIVE_NOVEL` | `novel init` or `novel-suite writer use <slug>` |
| `DOCTOR_FAIL` skills_* | Run `platforms/install-skills.ps1` for your IDE |
| Gate `PHASE0_NOT_COMPLETE` | Complete market scan + concept + init with `--concept` |
| `relations check` missing | Use `novel-suite writer gate`; legacy `relations check` via `novel_cli.py` when installed |
| JSON parse error | Ensure `pip install -e .` for `novel-suite` |

Legacy IDE flows unchanged: `.cursor/skills`, `.trae/skills`, `.qoder/skills`.
