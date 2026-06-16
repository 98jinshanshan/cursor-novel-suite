"""CLI handlers for video-production adapter dry-run (C5)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable

from novel_suite.core import errors as E
from novel_suite.core.contracts import novel_suite_root
from novel_suite.core.paths import suite_root
from novel_suite.core.result import Result, artifact, error_result, ok_result
from novel_suite.video_production.adapters import (
    AdapterPolicyError,
    run_comfyui_dry_run,
    run_davinci_dry_run,
    run_otio_dry_run,
)

_SAFE_EXAMPLE = re.compile(r"^[\w\u4e00-\u9fff\-]+$", re.UNICODE)
_ADAPTERS: dict[str, Callable[[Path, Path], dict[str, Any]]] = {
    "comfyui": run_comfyui_dry_run,
    "otio": run_otio_dry_run,
    "davinci": run_davinci_dry_run,
}


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def resolve_example_handoff_dir(example: str) -> Path:
    """Resolve read-only handoff sample directory under novel-suite/video-production/examples."""
    name = (example or "").strip()
    if not name or not _SAFE_EXAMPLE.match(name):
        raise ValueError(f"{E.VIDEO_PRODUCTION_EXAMPLE_INVALID}: invalid example name {example!r}")
    if ".." in name or "/" in name or "\\" in name:
        raise ValueError(f"{E.VIDEO_PRODUCTION_EXAMPLE_INVALID}: path traversal rejected")

    handoff = novel_suite_root() / "video-production" / "examples" / name / "handoff"
    if not handoff.is_dir():
        raise FileNotFoundError(f"{E.VIDEO_PRODUCTION_EXAMPLE_NOT_FOUND}: {handoff}")
    return handoff.resolve()


def resolve_output_dir(output: str | Path | None) -> Path:
    root = suite_root()
    if output is None or str(output).strip() == "":
        return (root / ".tmp" / "novel-suite-c5").resolve()
    out = Path(output)
    if not out.is_absolute():
        out = (root / out).resolve()
    try:
        out.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"{E.VIDEO_PRODUCTION_OUTPUT_OUT_OF_BOUNDS}: {out}") from exc
    return out


def run_adapter_dry_run(adapter: str, example: str, output: str | Path | None) -> Result:
    """Execute default-off dry-run for a single adapter skeleton."""
    key = (adapter or "").strip().lower()
    if key not in _ADAPTERS:
        return error_result(
            E.VIDEO_PRODUCTION_ADAPTER_UNKNOWN,
            f"Unknown adapter {adapter!r}; allowed: comfyui, otio, davinci",
            required=list(_ADAPTERS.keys()),
        )

    try:
        handoff_dir = resolve_example_handoff_dir(example)
        output_dir = resolve_output_dir(output)
        plan = _ADAPTERS[key](handoff_dir, output_dir)
    except AdapterPolicyError as exc:
        return error_result(E.VIDEO_PRODUCTION_ADAPTER_POLICY_VIOLATION, str(exc))
    except FileNotFoundError as exc:
        return error_result(E.VIDEO_PRODUCTION_ADAPTER_DRY_RUN_FAIL, str(exc))
    except ValueError as exc:
        msg = str(exc)
        code = (
            E.VIDEO_PRODUCTION_EXAMPLE_INVALID
            if E.VIDEO_PRODUCTION_EXAMPLE_INVALID in msg
            else E.VIDEO_PRODUCTION_OUTPUT_OUT_OF_BOUNDS
            if E.VIDEO_PRODUCTION_OUTPUT_OUT_OF_BOUNDS in msg
            else E.VIDEO_PRODUCTION_ADAPTER_DRY_RUN_FAIL
        )
        return error_result(code, msg)

    root = suite_root()
    out_path = plan.get("output_path", "")
    return ok_result(
        E.VIDEO_PRODUCTION_ADAPTER_DRY_RUN_OK,
        f"Dry-run plan written for adapter {key}",
        artifacts=[artifact(_rel(root, Path(out_path)), kind="file", label=f"{key}_dry_run")],
        adapter=key,
        example=example,
        handoff_dir=_rel(root, handoff_dir),
        plan=plan,
    )
