# Local API Key Storage

Secrets **never** belong in git. Use `platforms/save-local-secret.ps1` on your workstation only.

## Save SiliconFlow key

```powershell
cd G:\CURSOR
powershell -File platforms/save-local-secret.ps1 -Provider siliconflow
```

Paste the key when prompted (hidden input). Stored at:

`platforms/data/local-secrets/siliconflow.json` (gitignored)

## Load in Python

```python
from local_secrets import get_siliconflow_api_key

key = get_siliconflow_api_key(require=True)
```

## Rules

- Do **not** pass keys on the command line (shell history).
- Do **not** commit `.env`, `platforms/data/`, or chat-pasted keys.
- Run `powershell -File platforms/scan-staged-secrets.ps1` before commit if unsure.
- CI blocks `save-local-secret.ps1` and `local_secrets` loaders.

## Rotate

If a key was pasted in chat or logs, rotate at the provider and re-run the save script.
