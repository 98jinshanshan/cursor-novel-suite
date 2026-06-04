"""Chapter draft/promote — toolized writing artifacts (Phase E)."""

from __future__ import annotations

import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

CHAPTER_MIN = 1
CHAPTER_MAX = 999

from novel_suite.core import errors as E
from novel_suite.core.path_safety import assert_chapter_input_path
from novel_suite.core.paths import writer_root
from novel_suite.core.result import Result, artifact, error_result, ok_result
from novel_suite.writer import gate
from novel_suite.writer._legacy import load_script_module


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def count_cjk_chars(text: str) -> int:
    """Count CJK unified ideographs (rough chapter word count for Chinese)."""
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def safe_chapter_slug(title: str) -> str:
    raw = title.strip()
    raw = re.sub(r'[<>:"/\\|?*]', "", raw)
    raw = re.sub(r"\s+", "", raw)
    return raw[:40] or "chapter"


def chapter_basename(chapter: int, title: str) -> str:
    return f"{int(chapter):02d}_{safe_chapter_slug(title)}.md"


def validate_chapter_number(chapter: int) -> Result | None:
    if chapter < CHAPTER_MIN or chapter > CHAPTER_MAX:
        return error_result(
            E.INVALID_CHAPTER_NUMBER,
            f"Chapter number must be {CHAPTER_MIN}..{CHAPTER_MAX}, got {chapter}",
            next_actions=[f"Use --chapter between {CHAPTER_MIN} and {CHAPTER_MAX}"],
        )
    return None


def skip_gate_allowed() -> bool:
    return os.environ.get(E.ENV_ALLOW_SKIP_GATE, "").strip() == "1"


def assert_under_project(project: Path, target: Path) -> Path:
    resolved = target.resolve()
    root = project.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{E.PROJECT_PATH_OUT_OF_BOUNDS}: path escapes project root") from exc
    return resolved


def _templates_dir() -> Path:
    return writer_root() / "templates"


def _default_snapshot(chapter: int) -> str:
    tpl = _templates_dir() / "snapshot-chapter.md"
    if tpl.is_file():
        body = tpl.read_text(encoding="utf-8")
        nn = f"{int(chapter):02d}"
        return body.replace("{{N}}", str(chapter)).replace("{{NN}}", nn)
    return f"# 快照 — 第{chapter}章后\n\n## 状态变更\n\n-\n"


def update_progress_json(
    project: Path,
    *,
    chapter: int,
    title: str,
    filename: str,
    word_count: int,
) -> Path:
    progress_path = project / "canon" / "progress.json"
    if progress_path.is_file():
        data = json.loads(progress_path.read_text(encoding="utf-8"))
    else:
        story_title = project.name
        story = project / "story.md"
        if story.is_file():
            for line in story.read_text(encoding="utf-8").splitlines():
                if line.startswith("# "):
                    story_title = line[2:].strip()
                    break
        data = {"title": story_title, "chapters": [], "total_words": 0}

    rel_file = f"chapters/{filename}"
    entry = {
        "number": int(chapter),
        "file": rel_file,
        "title": title,
        "status": "draft",
        "word_count": word_count,
    }
    chapters: list[dict] = list(data.get("chapters") or [])
    replaced = False
    for i, ch in enumerate(chapters):
        if ch.get("number") == chapter:
            chapters[i] = {**ch, **entry}
            replaced = True
            break
    if not replaced:
        chapters.append(entry)
    data["chapters"] = sorted(chapters, key=lambda c: int(c.get("number", 0)))
    data["total_words"] = sum(int(c.get("word_count") or 0) for c in data["chapters"])
    data["updated_at"] = _utc_now()
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    progress_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return progress_path


def update_chapters_index(
    project: Path,
    *,
    chapter: int,
    title: str,
    filename: str,
    status: str = "draft",
) -> Path:
    index_path = project / "chapters" / "_index.md"
    num = f"{int(chapter):02d}"
    row = f"| {num} | {title} | {status} | [{filename}](./{filename}) |"
    if index_path.is_file():
        lines = index_path.read_text(encoding="utf-8").splitlines()
        out: list[str] = []
        replaced = False
        for line in lines:
            if line.startswith(f"| {num} ") or line.startswith(f"| {chapter} "):
                out.append(row)
                replaced = True
            else:
                out.append(line)
        if not replaced:
            if not any(l.startswith("| ---") for l in out):
                out.append("| 章 | 标题 | 状态 | 文件 |")
                out.append("| --- | --- | --- | --- |")
            out.append(row)
        index_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    else:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(
            "# 章节索引\n\n| 章 | 标题 | 状态 | 文件 |\n| --- | --- | --- | --- |\n" + row + "\n",
            encoding="utf-8",
        )
    return index_path


def write_phase5_manifest(project: Path) -> Path:
    nec = load_script_module("node_completion")
    manifest = nec.build_project_phase5_manifest(project=project)
    path = project / "canon" / "nodes" / "phase-5.completion.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    nec.write_manifest(path, manifest)
    return path


def validate_progress_against_schema(project: Path) -> list[str]:
    progress_path = project / "canon" / "progress.json"
    if not progress_path.is_file():
        return ["missing progress.json"]
    pg = load_script_module("pipeline_gate")
    data = json.loads(progress_path.read_text(encoding="utf-8"))
    return pg.validate_json_data(data, "progress.schema.json", label="progress.json")


def run_chapter_draft(
    project: Path,
    *,
    chapter: int,
    title: str,
    input_path: Path,
    snapshot_input: Path | None = None,
    snapshot_input_given: bool = False,
    skip_gate: bool = False,
    force: bool = False,
) -> Result:
    project = project.resolve()
    if not project.is_dir():
        return error_result(E.PROJECT_NOT_FOUND, f"Not a directory: {project}")

    invalid = validate_chapter_number(chapter)
    if invalid is not None:
        return invalid

    if skip_gate and not skip_gate_allowed():
        return error_result(
            E.SKIP_GATE_NOT_ALLOWED,
            "Skipping Phase 5 gate is not allowed",
            next_actions=[f"Unset --skip-gate, or set {E.ENV_ALLOW_SKIP_GATE}=1 for tests only"],
        )

    if snapshot_input_given:
        if snapshot_input is None or not Path(snapshot_input).is_file():
            path = snapshot_input or "(none)"
            return error_result(
                E.SNAPSHOT_INPUT_NOT_FOUND,
                f"Snapshot input file not found: {path}",
                next_actions=["Fix --snapshot-input path or omit the flag"],
            )

    if not skip_gate:
        gate_result = gate.run_gate(project, 5)
        if gate_result.status != "ok":
            return error_result(
                E.GATE_PHASE5_BLOCKED,
                "Cannot draft chapter: Phase 5 gate not satisfied",
                required=gate_result.required,
                next_actions=gate_result.next_actions or gate_result.details.get("next_actions", []),
                artifacts=gate_result.artifacts,
            )

    if not input_path.is_file():
        return error_result(
            E.CHAPTER_INPUT_NOT_FOUND,
            f"Input file not found: {input_path}",
            next_actions=["Provide --input path to chapter markdown"],
        )

    try:
        input_path = assert_chapter_input_path(project, input_path)
    except ValueError as exc:
        return error_result(
            E.CHAPTER_INPUT_OUT_OF_BOUNDS,
            str(exc),
            next_actions=[
                "Put draft under project outlines/ or chapters/.drafts/",
                "Or use a file under system TEMP/TMP",
            ],
        )

    body = input_path.read_text(encoding="utf-8")
    word_count = count_cjk_chars(body)
    filename = chapter_basename(chapter, title)
    chapter_path = assert_under_project(project, project / "chapters" / filename)
    if chapter_path.is_file() and not force:
        rel = str(chapter_path.relative_to(project)).replace("\\", "/")
        return error_result(
            E.CHAPTER_ALREADY_EXISTS,
            f"Chapter file already exists: {rel}",
            next_actions=[
                "Use --force to overwrite",
                "Use a new --chapter number",
                "Write to chapters/.drafts/ and use chapter promote",
            ],
            artifacts=[artifact(rel, label="chapter")],
        )

    chapter_path.parent.mkdir(parents=True, exist_ok=True)
    chapter_path.write_text(body if body.endswith("\n") else body + "\n", encoding="utf-8")

    snap_name = f"ch{int(chapter):02d}-after.md"
    snap_path = assert_under_project(project, project / "canon" / "snapshots" / snap_name)
    snap_path.parent.mkdir(parents=True, exist_ok=True)
    if snapshot_input_given and snapshot_input is not None:
        snap_path.write_text(snapshot_input.read_text(encoding="utf-8"), encoding="utf-8")
    elif not snap_path.is_file():
        snap_path.write_text(_default_snapshot(chapter), encoding="utf-8")

    progress_path = update_progress_json(
        project, chapter=chapter, title=title, filename=filename, word_count=word_count
    )
    index_path = update_chapters_index(
        project, chapter=chapter, title=title, filename=filename
    )
    manifest_path = write_phase5_manifest(project)

    rel = lambda p: str(p.relative_to(project)).replace("\\", "/")
    return ok_result(
        "CHAPTER_DRAFT_OK",
        f"Chapter {chapter} written ({word_count} CJK chars)",
        artifacts=[
            artifact(rel(chapter_path), label="chapter"),
            artifact(rel(snap_path), label="snapshot"),
            artifact(rel(progress_path), label="progress"),
            artifact(rel(index_path), label="index"),
            artifact(rel(manifest_path), label="phase-5.completion"),
        ],
        next_actions=[
            "novel-suite writer gate --phase 6 --json",
            "Run novel-review for reviews/chNN-review.md",
        ],
        chapter=chapter,
        word_count=word_count,
        filename=filename,
    )


def run_chapter_promote(project: Path, *, chapter_file: str) -> Result:
    project = project.resolve()
    name = Path(chapter_file).name
    draft = assert_under_project(project, project / "chapters" / ".drafts" / name)
    if not draft.is_file():
        return error_result(
            E.DRAFT_NOT_FOUND,
            f"Draft not found: {draft}",
            next_actions=[f"Save draft to chapters/.drafts/{name} first"],
        )
    target = assert_under_project(project, project / "chapters" / name)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(draft, target)
    rel = str(target.relative_to(project)).replace("\\", "/")
    return ok_result(
        "CHAPTER_PROMOTE_OK",
        f"Promoted {name}",
        artifacts=[artifact(rel, label="chapter")],
    )
