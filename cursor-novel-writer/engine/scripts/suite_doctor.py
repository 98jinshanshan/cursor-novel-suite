#!/usr/bin/env python3
"""Health check for Novel Suite workspace (skills, roots, engine)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parents[1]
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from scripts import suite_paths as sp

EXPECTED_WRITER_SKILLS = {
    "chapter-writing",
    "character-management",
    "novel-export",
    "novel-market-scan",
    "novel-marketing",
    "novel-pipeline",
    "novel-review",
    "plot-structure",
    "story-init",
    "worldbuilding",
}

SKILL_INSTALL_DIRS = {
    "cursor": [".agents/skills", ".cursor/skills"],
    "qoder": [".qoder/skills"],
    "trae-cn": [".trae/skills"],
}


def _check(name: str, ok: bool, detail: str = "") -> dict:
    return {"name": name, "ok": ok, "detail": detail}


def _skill_names(path: Path) -> set[str]:
    if not path.is_dir():
        return set()
    return {p.name for p in path.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()}


def run_doctor(*, core_only: bool = False) -> tuple[list[dict], int]:
    checks: list[dict] = []
    exit_code = 0

    try:
        root = sp.suite_root()
        checks.append(_check("suite_root", True, str(root)))
    except SystemExit as exc:
        checks.append(_check("suite_root", False, str(exc)))
        return checks, 1

    writer = root / sp.WRITER_DIR / "engine" / "novel_cli.py"
    video = root / sp.VIDEO_DIR / "engine" / "video_cli.py"
    checks.append(_check("writer_engine", writer.is_file(), str(writer)))
    checks.append(_check("video_engine", video.is_file(), str(video)))
    checks.append(_check("marker", (root / sp.MARKER).is_file(), sp.MARKER))
    checks.append(_check("novels_dir", (root / "novels").is_dir(), "novels/"))
    checks.append(_check("intel_dir", (root / "intel").is_dir(), "intel/"))
    checks.append(_check("agents_md", (root / "AGENTS.md").is_file(), "AGENTS.md"))

    src_skills = root / sp.WRITER_DIR / "skills"
    src_names = _skill_names(src_skills)
    missing_src = EXPECTED_WRITER_SKILLS - src_names
    checks.append(
        _check(
            "writer_skills_source",
            not missing_src,
            f"{len(src_names)} skills"
            + (f"; missing: {sorted(missing_src)}" if missing_src else ""),
        )
    )

    for platform, rel_dirs in SKILL_INSTALL_DIRS.items():
        if core_only:
            continue
        for rel in rel_dirs:
            installed = root / Path(rel)
            names = _skill_names(installed)
            missing = EXPECTED_WRITER_SKILLS - names
            ok = len(missing) == 0
            checks.append(
                _check(
                    f"skills_{platform}_{rel.replace('/', '_')}",
                    ok,
                    f"{len(names)} installed"
                    + (f"; missing: {sorted(missing)}" if missing else ""),
                )
            )

    scan_wrapper = src_skills / "novel-market-scan" / "scripts" / "intel_scan.py"
    checks.append(_check("intel_scan_wrapper", scan_wrapper.is_file(), str(scan_wrapper)))

    active = root / "novels" / ".active"
    if active.is_file():
        checks.append(_check("active_novel", True, active.read_text(encoding="utf-8").strip()))
    else:
        checks.append(_check("active_novel", True, "(none — run novel init)"))

    for c in checks:
        if not c["ok"]:
            exit_code = 1
    return checks, exit_code


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Novel Suite workspace doctor")
    ap.add_argument("--json", action="store_true", help="Emit JSON")
    ap.add_argument(
        "--core-only",
        action="store_true",
        help="Skip IDE skill install dirs (for CI)",
    )
    args = ap.parse_args()
    checks, code = run_doctor(core_only=args.core_only)
    if args.json:
        print(json.dumps({"ok": code == 0, "checks": checks}, ensure_ascii=False, indent=2))
    else:
        for c in checks:
            mark = "OK" if c["ok"] else "FAIL"
            detail = f" — {c['detail']}" if c["detail"] else ""
            print(f"{mark}: {c['name']}{detail}")
        if code == 0:
            print("\nDoctor: all checks passed.")
        else:
            print("\nDoctor: fix FAIL items (see docs/verification/trae-cn.md).", file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
