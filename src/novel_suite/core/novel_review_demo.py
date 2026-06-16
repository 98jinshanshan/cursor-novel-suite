"""Novel review demo — offline novel.review runner (no auto-rewrite, no project write)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from novel_suite.core.contracts import novel_suite_root
from novel_suite.core.errors import (
    NOVEL_REVIEW_DEMO_RUN_OK,
    NOVEL_REVIEW_DEMO_VALIDATE_FAIL,
    NOVEL_REVIEW_DEMO_VALIDATE_OK,
)
from novel_suite.core.paths import suite_root
from novel_suite.core.result import artifact, error_result, ok_result, Result

_DEMO_DIR = "novel-review-demo"
_MANIFEST = "novel-review-demo.sample.json"

_ARTIFACT_PATHS: dict[str, str] = {
    "review_summary.md": "novel-suite/novel-review-demo/review_summary.md",
    "continuity_check.md": "novel-suite/novel-review-demo/continuity_check.md",
    "deai_checklist.md": "novel-suite/novel-review-demo/deai_checklist.md",
    "revision_suggestions.md": "novel-suite/novel-review-demo/revision_suggestions.md",
    "risk_notes.md": "novel-suite/novel-review-demo/risk_notes.md",
    "review_handoff_manifest.json": "novel-suite/novel-review-demo/review_handoff_manifest.json",
}

_CORE_FILES = (
    "README.md",
    "schema.json",
    _MANIFEST,
    "demo_chapter_excerpt.md",
    "review_summary.md",
    "continuity_check.md",
    "deai_checklist.md",
    "revision_suggestions.md",
    "risk_notes.md",
    "review_handoff_manifest.json",
)


def novel_review_demo_root() -> Path:
    return novel_suite_root() / _DEMO_DIR


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def validate_novel_review_demo() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    demo = novel_review_demo_root()
    for name in _CORE_FILES:
        p = demo / name
        checks.append(
            {
                "name": f"novel_review_demo.{name.replace('/', '.')}",
                "ok": p.is_file(),
                "path": _rel(root, p),
            }
        )
    for logical, rel in _ARTIFACT_PATHS.items():
        p = root / rel
        checks.append(
            {
                "name": f"novel_review_demo.artifact.{logical}",
                "ok": p.is_file(),
                "path": _rel(root, p),
            }
        )
    manifest = demo / _MANIFEST
    if manifest.is_file():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            blocked = (
                data.get("commercial_release_allowed") is False
                and data.get("verdict") == "blocked"
                and data.get("adapter_enabled") is False
                and data.get("external_call_performed") is False
                and data.get("auto_rewrite_allowed") is False
            )
            checks.append(
                {
                    "name": "novel_review_demo.manifest_blocked",
                    "ok": blocked,
                    "path": _rel(root, manifest),
                }
            )
        except json.JSONDecodeError as exc:
            checks.append(
                {
                    "name": "novel_review_demo.manifest_json",
                    "ok": False,
                    "path": _rel(root, manifest),
                    "details": [str(exc)],
                }
            )
    rev = demo / "revision_suggestions.md"
    if rev.is_file():
        text = rev.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "novel_review_demo.suggestions_not_auto_rewrite",
                "ok": "建议" in text and ("不自动" in text or "不自动改稿" in text),
                "path": _rel(root, rev),
            }
        )
    return checks


def run_novel_review_demo_validate() -> Result:
    checks = validate_novel_review_demo()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            NOVEL_REVIEW_DEMO_VALIDATE_FAIL,
            f"Novel review demo: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
            verdict="blocked",
        )
    return ok_result(
        NOVEL_REVIEW_DEMO_VALIDATE_OK,
        "Novel review demo validation passed (6 artifacts; no auto-rewrite)",
        checks=checks,
        artifact_count=6,
        commercial_release_allowed=False,
        verdict="blocked",
        adapter_enabled=False,
        external_call_performed=False,
        auto_rewrite_allowed=False,
        next_actions=[
            "novel-suite novel-review-demo run --json",
            "POST /api/agents/novel-review/run",
        ],
    )


def run_novel_review_demo() -> Result:
    validate = run_novel_review_demo_validate()
    if validate.status != "ok":
        return validate

    root = suite_root()
    arts: list[dict[str, Any]] = []
    for logical, rel in _ARTIFACT_PATHS.items():
        p = root / rel
        arts.append(artifact(_rel(root, p), kind="file", label=logical))

    return ok_result(
        NOVEL_REVIEW_DEMO_RUN_OK,
        "Novel review offline demo complete (suggestions only; no project write)",
        artifacts=arts,
        demo_input="novel-suite/novel-review-demo/demo_chapter_excerpt.md",
        adapter_enabled=False,
        external_call_performed=False,
        auto_rewrite_allowed=False,
        commercial_release_allowed=False,
        verdict="blocked",
        run_status="ok",
        next_actions=[
            "Read revision_suggestions.md — apply edits manually",
            "novel-suite commercial-release-candidate validate --json",
        ],
        run_blockers=[],
    )
