"""Read platform config from project.json — single source of truth."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from novel_suite.platforms._registry import get_platform


def get_target_platform(project: Path) -> str:
    """从 project.json 读取目标发布平台。

    返回：平台名（如 "fanqie"），如果未设置则返回 "通用"
    """
    project_json = project / "canon" / "project.json"
    if not project_json.is_file():
        return "通用"
    try:
        data = json.loads(project_json.read_text(encoding="utf-8"))
        return data.get("platform_target", "通用")
    except (json.JSONDecodeError, OSError):
        return "通用"


def get_platform_config(project: Path) -> dict[str, Any]:
    """获取目标平台的完整配置（从注册表读取）。"""
    target = get_target_platform(project)
    platform_info = get_platform(target)
    if platform_info is None:
        return {"platform_target": target, "found": False}
    return {"platform_target": target, "found": True, "config": platform_info}
