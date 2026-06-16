"""Tests for platform registry (Sprint 4 Phase A)."""

from __future__ import annotations

from novel_suite.platforms._registry import (
    get_platform,
    list_platform_keys,
    list_platforms,
    validate_platform,
)


def test_list_platforms_count():
    assert len(list_platforms()) == 6


def test_list_platform_keys_sorted():
    keys = list_platform_keys()
    assert keys == sorted(keys)
    assert "douyin" in keys
    assert "fanqie" in keys


def test_list_platforms_filter_video():
    video = list_platforms(platform_type="video")
    assert len(video) == 3
    assert all(p["type"] == "video" for p in video)


def test_list_platforms_filter_novel():
    novel = list_platforms(platform_type="novel")
    assert len(novel) == 3
    assert all(p["type"] == "novel" for p in novel)


def test_get_platform_douyin():
    p = get_platform("douyin")
    assert p is not None
    assert p["aspect"] == "9:16"
    assert p["auth_type"] == "oauth2_cookie"


def test_get_platform_unknown():
    assert get_platform("unknown") is None


def test_validate_platform():
    assert validate_platform("bilibili") is True
    assert validate_platform("INVALID") is False
