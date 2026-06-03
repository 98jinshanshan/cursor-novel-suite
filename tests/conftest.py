"""Shared fixtures for Novel Suite 2.0 package tests."""

from __future__ import annotations

import os
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
