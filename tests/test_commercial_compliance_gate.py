"""B4 commercial release compliance — static gate tests."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

from novel_suite.core.compliance import check_commercial_release_gate

REPO = Path(__file__).resolve().parents[1]


def _load_pyproject() -> dict:
    return tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))


def _dep_names(deps: list[str]) -> set[str]:
    names: set[str] = set()
    for line in deps:
        name = re.split(r"[<>=!~\[]", line.strip())[0].strip().lower()
        if name:
            names.add(name)
    return names


def test_pyproject_runtime_no_ebooklib():
    project = _load_pyproject()["project"]
    assert "ebooklib" not in _dep_names(project.get("dependencies", []))


def test_pyproject_dev_no_ebooklib():
    optional = _load_pyproject()["project"].get("optional-dependencies", {})
    assert "ebooklib" not in _dep_names(optional.get("dev", []))


def test_pyproject_epub_extra_has_ebooklib():
    optional = _load_pyproject()["project"].get("optional-dependencies", {})
    assert "ebooklib" in _dep_names(optional.get("epub", []))


def test_third_party_notices_keywords(repo_root: Path):
    text = (repo_root / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    for kw in (
        "ebooklib",
        "edge-tts",
        "FFmpeg",
        "Stable Diffusion",
        "ControlNet",
        "MediaCrawler",
    ):
        assert kw.lower() in text.lower() or kw in text, kw
    assert "OAuth" in text or "平台" in text


def test_third_party_policy_phrases(repo_root: Path):
    text = (repo_root / "THIRD_PARTY_POLICY.md").read_text(encoding="utf-8")
    for phrase in ("默认关闭", "禁入商业核心", "人工确认"):
        assert phrase in text, phrase


def test_commercial_release_gate_file(repo_root: Path):
    gate = repo_root / "COMMERCIAL_RELEASE_GATE.md"
    assert gate.is_file()
    text = gate.read_text(encoding="utf-8")
    assert "待法律" in text or "待人工法律" in text
    assert "不允许" in text


def test_readme_boundary_phrases(repo_root: Path):
    text = (repo_root / "README.md").read_text(encoding="utf-8")
    assert "默认关闭" in text
    assert "人工确认" in text
    idx = text.find("publish upload")
    assert idx >= 0
    window = text[max(0, idx - 500) : idx + 300]
    assert "默认关闭" in window or "人工确认" in window or "可选适配器" in window


def test_check_commercial_release_gate_all_pass(repo_root: Path):
    checks = check_commercial_release_gate()
    failed = [c for c in checks if not c.get("ok")]
    assert not failed, failed
