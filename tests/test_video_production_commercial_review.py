"""Tests for C6/C7 commercial preflight (read-only)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.commercialization import (
    run_commercial_review_validate,
    validate_commercial_review,
)


def test_c6_docs_exist(repo_root: Path):
    checks = validate_commercial_review()
    c6 = [c for c in checks if "commercial-review" in c.get("path", c.get("name", ""))]
    failed = [c for c in checks if not c.get("ok")]
    assert not failed, failed
    assert len(c6) >= 10


def test_c7_docs_exist(repo_root: Path):
    checks = validate_commercial_review()
    names = {c["name"] for c in checks}
    assert any("commercialization" in n for n in names)


def test_sample_manifest_verdict_and_assets(repo_root: Path):
    manifest_path = (
        repo_root
        / "novel-suite"
        / "video-production"
        / "commercial-review"
        / "sample-package-manifest.sample.json"
    )
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["verdict"] in ("demo_only", "blocked", "needs_manual_review")
    assert data["verdict"] != "commercial_ready"
    assert data["commercial_blocked"] is True
    required = {
        "asset_id",
        "source_type",
        "license_status",
        "commercial_allowed",
        "upload_allowed",
        "review_status",
        "risk_level",
    }
    for asset in data["assets"]:
        assert required.issubset(asset.keys()), asset


def test_release_blockers_declares_not_allowed(repo_root: Path):
    text = (
        repo_root
        / "novel-suite"
        / "video-production"
        / "commercial-review"
        / "release-blockers.md"
    ).read_text(encoding="utf-8")
    assert "不允许" in text or "仍不允许" in text


def test_claims_forbidden_blocks_misleading(repo_root: Path):
    text = (
        repo_root / "novel-suite" / "commercialization" / "claims-forbidden.md"
    ).read_text(encoding="utf-8")
    assert "一键" in text or "高质量" in text
    assert "商业发布" in text or "已可" in text


def test_handoff_asset_manifest_fields(repo_root: Path):
    data = json.loads(
        (
            repo_root
            / "novel-suite"
            / "video-production"
            / "examples"
            / "cold_case_echo_short_drama"
            / "handoff"
            / "asset_manifest.sample.json"
        ).read_text(encoding="utf-8")
    )
    required = {
        "asset_id",
        "source_type",
        "license_status",
        "commercial_allowed",
        "upload_allowed",
        "review_status",
        "risk_level",
    }
    for asset in data["assets"]:
        assert required.issubset(asset.keys()), asset
    assert data["commercial_blocked"] is True


def test_run_commercial_review_validate_ok():
    result = run_commercial_review_validate()
    assert result.status == "ok"
    assert result.code == E.COMMERCIAL_REVIEW_VALIDATE_OK
    assert result.details.get("commercial_release_allowed") is False


def test_cli_commercial_review_validate(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "novel_suite.cli",
            "commercial-review",
            "validate",
            "--json",
        ],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    data = json.loads(r.stdout)
    assert data["status"] == "ok"
    assert data["code"] == E.COMMERCIAL_REVIEW_VALIDATE_OK
    assert data["details"]["commercial_release_allowed"] is False
