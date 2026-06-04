"""Shared fixtures for Novel Suite 2.0 package tests."""

from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _novel_suite_root_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NOVEL_SUITE_ROOT", str(REPO_ROOT))


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def demo_project(repo_root: Path) -> Path:
    return repo_root / "cursor-novel-writer" / "examples" / "demo-novel"


@pytest.fixture
def novels_scratch(repo_root: Path) -> Path:
    """Writable novel project under novels/ (satisfies path-bound checks)."""
    slug = f"_pytest-{uuid.uuid4().hex[:8]}"
    root = repo_root / "novels" / slug
    root.mkdir(parents=True)
    yield root
    if root.is_dir():
        shutil.rmtree(root, ignore_errors=True)
