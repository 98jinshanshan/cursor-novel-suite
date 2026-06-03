"""Gate structured results against demo-novel."""

from __future__ import annotations

from novel_suite.core import errors as E
from novel_suite.writer import gate


def test_demo_gate_phase1_ok(demo_project):
    result = gate.run_gate(demo_project, 1)
    assert result.status == "ok"
    assert result.code == "GATE_OK"


def test_empty_project_gate_phase1_fails(repo_root: Path):
    """Failure path: project without Phase 0 completion."""
    import novel_suite.writer.registry as reg

    novels = repo_root / "novels"
    novels.mkdir(exist_ok=True)
    proj = novels / "empty-gate-test"
    proj.mkdir(exist_ok=True)
    (proj / "task_plan.md").write_text("- [ ] Phase 0: x\n", encoding="utf-8")
    entry = {
        "slug": "empty-gate-test",
        "path": "novels/empty-gate-test",
        "title": "Empty",
    }
    data = reg.load_registry()
    data["novels"] = [n for n in data.get("novels", []) if n.get("slug") != "empty-gate-test"]
    data["novels"].append(entry)
    reg.save_registry(data)
    result = gate.run_gate(proj, 1)
    assert result.status == "error"
    assert result.code in ("PHASE0_NOT_COMPLETE", "GATE_FAIL", "MISSING_CONCEPT_BRIEF")
    assert result.next_actions


def test_classify_phase0():
    assert gate.classify_error("Phase 0 not complete in task_plan.md") == E.PHASE0_NOT_COMPLETE


def test_classify_blockers():
    assert gate.classify_error("open blockers in ch01-review.md") == E.OPEN_REVIEW_BLOCKERS
