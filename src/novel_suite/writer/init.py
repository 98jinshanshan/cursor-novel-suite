"""Novel project init — wraps legacy novel_cli.scaffold_project."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
from pathlib import Path
from typing import Any

from novel_suite.core import errors as E
from novel_suite.core.paths import suite_root, writer_root
from novel_suite.core.json_stdout import capture_legacy_output
from novel_suite.core.result import Result, artifact, error_result, ok_result
from novel_suite.writer import gate, registry
from novel_suite.writer._legacy import load_script_module


def _load_novel_cli_module():
    engine = writer_root() / "engine"
    path = engine / "novel_cli.py"
    if not path.is_file():
        raise FileNotFoundError(path)
    name = "novel_suite_legacy_novel_cli"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    saved = sys.path[:]
    eng = str(engine)
    if eng not in sys.path:
        sys.path.insert(0, eng)
    try:
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.path[:] = saved


def resolve_init_paths(
    *,
    title: str,
    slug: str = "",
    output: Path | None = None,
) -> tuple[Path, str, bool]:
    """Return (project_path, slug, register_in_registry)."""
    out_arg = None if output is None else str(output).replace("\\", "/")
    if out_arg is None or out_arg in (".", "./my-novel", "my-novel"):
        path, auto_slug = registry.default_novel_path(title)
        if slug:
            used = registry.list_slugs()
            final_slug = slug if slug not in used else registry.allocate_slug(slug)
            path = registry._novels_dir() / final_slug
            auto_slug = final_slug
        return path, auto_slug, True
    assert output is not None
    path = output.resolve()
    final_slug = slug or registry.allocate_slug(registry.slug_from_title(title))
    under_novels = False
    try:
        path.resolve().relative_to(registry._novels_dir().resolve())
        under_novels = True
    except ValueError:
        pass
    return path, final_slug, under_novels


def resolve_concept_path(concept: Path | None) -> Path | None:
    if concept is None:
        return None
    p = concept.expanduser()
    if not p.is_absolute():
        p = (suite_root() / p).resolve()
    else:
        p = p.resolve()
    return p


def finalize_project_phase0_manifest(project: Path) -> None:
    """Align project phase-0 manifest with gate when concept + suite intel are ready."""
    nec = load_script_module("node_completion")
    path = nec.completion_path_for_project(project, 0)
    if not path.is_file():
        return
    manifest = nec.load_manifest(path)
    if not manifest:
        return
    nec._mark_subtasks_done(manifest, frozenset({"P0-S5", "P0-S6"}))
    if not nec.validate_phase0_intel_for_gate():
        nec._mark_subtasks_done(
            manifest,
            frozenset({"P0-S0", "P0-S1", "P0-S2", "P0-S3", "P0-S4"}),
        )
    manifest["status"] = "complete"
    if not manifest.get("completed_at"):
        manifest["completed_at"] = nec.utc_now()
    nec.write_manifest(path, manifest)


def collect_init_artifacts(project: Path, root: Path) -> list[dict[str, Any]]:
    rel = lambda p: artifact(_rel(root, p), label="file") if p.is_file() else None
    paths = [
        (project, "project"),
        (project / "story.md", "story"),
        (project / "canon" / "project.json", "project_json"),
        (project / "canon" / "progress.json", "progress"),
        (project / "canon" / "concept-brief.md", "concept_brief"),
        (project / "task_plan.md", "task_plan"),
    ]
    arts: list[dict[str, Any]] = []
    for path, label in paths:
        if path.is_dir():
            arts.append(artifact(_rel(root, path), kind="directory", label=label))
        elif path.is_file():
            arts.append(artifact(_rel(root, path), label=label))
    return arts


def run_init(
    *,
    title: str,
    premise: str,
    genre: str = "通用",
    slug: str = "",
    output: Path | None = None,
    concept: Path | None = None,
    platform_target: str = "通用",
    json_mode: bool = False,
) -> Result:
    if not title.strip():
        return error_result("INIT_TITLE_REQUIRED", "Title is required")
    if not premise.strip():
        return error_result("INIT_PREMISE_REQUIRED", "Premise is required")

    concept_path = resolve_concept_path(concept)
    if concept is not None and (concept_path is None or not concept_path.is_file()):
        return error_result(
            "CONCEPT_NOT_FOUND",
            f"Concept file not found: {concept}",
            next_actions=["Run writer scan --demo and pick intel/concepts/*.md"],
        )

    try:
        path, final_slug, register = resolve_init_paths(title=title, slug=slug, output=output)
    except Exception as exc:  # noqa: BLE001
        return error_result("INIT_PATH_ERROR", str(exc))

    cli = _load_novel_cli_module()
    legacy_output: list[str] = []
    try:
        if json_mode:
            with capture_legacy_output() as captured:
                cli.scaffold_project(
                    path,
                    title,
                    premise,
                    genre=genre,
                    slug=final_slug,
                    platform_target=platform_target,
                    register=register,
                    concept_path=concept_path,
                )
                legacy_output = captured
        else:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                cli.scaffold_project(
                    path,
                    title,
                    premise,
                    genre=genre,
                    slug=final_slug,
                    platform_target=platform_target,
                    register=register,
                    concept_path=concept_path,
                )
    except Exception as exc:  # noqa: BLE001
        return error_result(E.INIT_SCAFFOLD_FAILED, str(exc))

    root = suite_root()
    project = path.resolve()
    if concept_path is not None:
        finalize_project_phase0_manifest(project)
    arts = collect_init_artifacts(project, root)

    active = registry.get_active_slug()
    gate_result = gate.run_gate(project, 1)
    gate_ok = gate_result.status == "ok"
    try:
        project_rel = project.relative_to(root).as_posix()
    except ValueError:
        project_rel = str(project)

    details: dict[str, Any] = {
        "slug": final_slug,
        "project_path": str(project),
        "active_slug": active,
        "gate_phase_1": gate_ok,
        "gate_errors": gate_result.required if not gate_ok else [],
    }
    if legacy_output:
        details["legacy_output"] = legacy_output

    return ok_result(
        "INIT_OK",
        f"Initialized novel '{title}' as {final_slug}",
        artifacts=arts,
        next_actions=[
            f"novel-suite writer gate --phase 2 --project {project_rel} --json"
            if gate_ok
            else "Fix gate errors before Phase 2 (see gate_errors)",
            "Complete worldbuilding + characters (Phase 2)",
        ],
        **details,
    )


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)
