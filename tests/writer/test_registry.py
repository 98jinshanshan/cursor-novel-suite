"""Registry slug allocation and path bounds."""

from __future__ import annotations

import pytest

from novel_suite.core import errors as E
from novel_suite.writer import registry as reg


def test_slug_from_title_unicode():
    assert reg.slug_from_title("侯府春深")
    s = reg.slug_from_title("侯府春深")
    assert s.startswith("novel-")


def test_allocate_slug_unique():
    data = {"version": 1, "novels": [{"slug": "fog"}], "active_slug": None}
    assert reg.allocate_slug("fog", data) == "fog-2"


def test_assert_project_rejects_outside_novels(repo_root: Path, tmp_path: Path):
    outside = tmp_path / "escape"
    outside.mkdir()
    with pytest.raises(ValueError) as exc:
        reg.assert_project_in_allowed_roots(outside)
    assert E.PROJECT_PATH_OUT_OF_BOUNDS in str(exc.value)


def test_demo_project_allowed(demo_project):
    p = reg.assert_project_in_allowed_roots(demo_project)
    assert p == demo_project.resolve()
