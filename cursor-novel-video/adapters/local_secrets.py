#!/usr/bin/env python3
"""Load gitignored local secrets — workstation only, never commit keys."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

_LOCALHOST_MARKERS = ("127.0.0.1", "localhost", "::1")
_FORBIDDEN_FP_FILE = "platforms/secret-fingerprints.json"


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".novel-suite-root").is_file() or (parent / "platforms" / "final-verify.ps1").is_file():
            return parent
    return here.parents[2]


def assert_local_workstation() -> None:
    """Refuse in CI / cloud agents."""
    if os.environ.get("CI", "").lower() in ("1", "true", "yes"):
        raise RuntimeError("local_secrets: blocked in CI")
    if os.environ.get("GITHUB_ACTIONS", "").lower() == "true":
        raise RuntimeError("local_secrets: blocked in GitHub Actions")


def _secrets_path(provider: str) -> Path:
    return _repo_root() / "platforms" / "data" / "local-secrets" / f"{provider}.json"


def _load_json_secret(provider: str, env_var: str) -> str:
    assert_local_workstation()
    path = _secrets_path(provider)
    if not path.is_file():
        return ""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid secret file {path}: {exc}") from exc
    if not data.get("local_only"):
        raise RuntimeError(f"Secret file {path} missing local_only flag")
    key = str(data.get("key") or "").strip()
    if key:
        os.environ.setdefault(env_var, key)
    return key


def _check_forbidden_fingerprint(key: str) -> None:
    fp_path = _repo_root() / _FORBIDDEN_FP_FILE
    if not fp_path.is_file() or not key:
        return
    digest = hashlib.sha256(key.encode()).hexdigest()
    data = json.loads(fp_path.read_text(encoding="utf-8"))
    for entry in data.get("forbidden_sha256") or []:
        if entry.get("sha256") == digest:
            print(
                f"WARN: key matches blocked fingerprint {entry.get('id')} — local use only; rotate if leaked",
                file=sys.stderr,
            )


def get_siliconflow_api_key(*, require: bool = False) -> str:
    """SILICONFLOW_API_KEY from env or platforms/data/local-secrets/siliconflow.json."""
    assert_local_workstation()
    key = os.environ.get("SILICONFLOW_API_KEY", "").strip()
    if not key:
        key = _load_json_secret("siliconflow", "SILICONFLOW_API_KEY")
    if key:
        _check_forbidden_fingerprint(key)
    if require and not key:
        raise RuntimeError(
            "SILICONFLOW_API_KEY missing. Run: powershell -File platforms/save-local-secret.ps1 -Provider siliconflow"
        )
    return key


def get_ark_api_key(*, require: bool = False) -> str:
    assert_local_workstation()
    key = os.environ.get("ARK_API_KEY", "").strip()
    if not key:
        key = _load_json_secret("ark", "ARK_API_KEY")
    if require and not key:
        raise RuntimeError("ARK_API_KEY missing")
    return key
