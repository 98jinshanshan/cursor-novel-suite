"""Load optional novel-suite.toml from monorepo root."""

from __future__ import annotations

import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Any

from novel_suite.core.paths import suite_root

CONFIG_NAME = "novel-suite.toml"


@lru_cache(maxsize=1)
def load_config() -> dict[str, Any]:
    path = suite_root() / CONFIG_NAME
    if not path.is_file():
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError:
        return {}


def min_suite_version() -> str:
    cfg = load_config()
    ws = cfg.get("workspace", {})
    if isinstance(ws, dict):
        return str(ws.get("min_suite_version", "2026.06.03-nec"))
    return "2026.06.03-nec"
