"""Load cursor-novel-writer engine/scripts modules without duplicating NEC logic."""

from __future__ import annotations

import importlib.util
import sys
from functools import lru_cache
from pathlib import Path
from types import ModuleType

from novel_suite.core.paths import writer_root


@lru_cache(maxsize=1)
def _engine_dir() -> Path:
    return writer_root() / "engine"


def _ensure_engine_path() -> None:
    eng = str(_engine_dir())
    if eng not in sys.path:
        sys.path.insert(0, eng)


def load_script_module(stem: str) -> ModuleType:
    """Import `scripts/<stem>.py` from writer engine."""
    _ensure_engine_path()
    path = _engine_dir() / "scripts" / f"{stem}.py"
    if not path.is_file():
        raise FileNotFoundError(path)
    name = f"novel_suite_legacy_{stem}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod
