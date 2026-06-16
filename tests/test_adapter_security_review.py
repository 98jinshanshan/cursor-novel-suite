"""Tests for C8 adapter security review docs (read-only)."""

from __future__ import annotations

from pathlib import Path

from novel_suite.core.commercialization import validate_commercial_review


def test_c8_docs_exist(repo_root: Path):
    checks = validate_commercial_review()
    c8 = [c for c in checks if "adapter-security-review" in c.get("path", c.get("name", ""))]
    failed = [c for c in checks if not c.get("ok")]
    assert len(c8) >= 12, c8
    assert not failed, failed


def test_readiness_matrix_blocked_status(repo_root: Path):
    text = (
        repo_root
        / "novel-suite"
        / "video-production"
        / "adapter-security-review"
        / "adapter-readiness-matrix.md"
    ).read_text(encoding="utf-8")
    assert "blocked_until_C8_review_and_user_confirmation" in text
    assert "ComfyUI" in text
    assert "Platform publishing" in text


def test_activation_policy_no_silent_upgrade(repo_root: Path):
    text = (
        repo_root
        / "novel-suite"
        / "video-production"
        / "adapter-security-review"
        / "adapter-activation-policy.md"
    ).read_text(encoding="utf-8")
    assert "A1" in text
    assert "静默" in text or "禁止" in text
