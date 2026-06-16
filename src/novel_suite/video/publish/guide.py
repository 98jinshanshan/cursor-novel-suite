"""Publish step guides — machine-readable flows for agents and MCP clients."""

from __future__ import annotations

from typing import Any

from novel_suite.platforms._registry import get_platform, list_platform_keys, validate_platform

GUIDE_STEPS: dict[str, list[dict[str, Any]]] = {
    "douyin": [
        {
            "step": 1,
            "action": "auth.login",
            "description": "登录抖音创作者平台",
            "cli": "novel-suite auth login --platform douyin --json",
            "mcp_tool": "auth.login",
        },
        {
            "step": 2,
            "action": "video.pipeline",
            "description": "生成章节摘要视频",
            "cli": "novel-suite video pipeline --project <path> --chapter-key ch01 --mode proof --json",
            "mcp_tool": None,
        },
        {
            "step": 3,
            "action": "video.gate",
            "description": "门禁检查（合规 + 角色一致性）",
            "cli": "novel-suite video gate --project <path> --chapter-key ch01 --json",
            "mcp_tool": None,
        },
        {
            "step": 4,
            "action": "publish.upload",
            "description": "上传发布到抖音",
            "cli": "novel-suite video publish upload --project <path> --chapter-key ch01 --json",
            "mcp_tool": "publish.upload",
        },
    ],
    "kuaishou": [
        {
            "step": 1,
            "action": "auth.login",
            "description": "登录快手创作者平台",
            "cli": "novel-suite auth login --platform kuaishou --json",
            "mcp_tool": "auth.login",
        },
        {
            "step": 2,
            "action": "video.pipeline",
            "description": "生成竖屏摘要视频",
            "cli": "novel-suite video pipeline --project <path> --chapter-key ch01 --json",
            "mcp_tool": None,
        },
        {
            "step": 3,
            "action": "video.gate",
            "description": "门禁检查",
            "cli": "novel-suite video gate --project <path> --chapter-key ch01 --platform kuaishou --json",
            "mcp_tool": None,
        },
        {
            "step": 4,
            "action": "publish.upload",
            "description": "上传发布到快手",
            "cli": "novel-suite video publish upload --project <path> --platform kuaishou --json",
            "mcp_tool": "publish.upload",
        },
    ],
    "bilibili": [
        {
            "step": 1,
            "action": "auth.login",
            "description": "登录 B 站创作中心",
            "cli": "novel-suite auth login --platform bilibili --json",
            "mcp_tool": "auth.login",
        },
        {
            "step": 2,
            "action": "video.pipeline",
            "description": "生成 16:9 解说视频",
            "cli": "novel-suite video compose --project <path> --aspect 16:9 --json",
            "mcp_tool": None,
        },
        {
            "step": 3,
            "action": "video.gate",
            "description": "门禁检查",
            "cli": "novel-suite video gate --project <path> --platform bilibili --json",
            "mcp_tool": None,
        },
        {
            "step": 4,
            "action": "publish.upload",
            "description": "上传发布到 B 站",
            "cli": "novel-suite video publish upload --project <path> --platform bilibili --json",
            "mcp_tool": "publish.upload",
        },
    ],
    "fanqie": [
        {
            "step": 1,
            "action": "auth_login",
            "description": "配置番茄 API Key（需设置 FANQIE_API_KEY 环境变量）",
            "cli": "novel-suite auth login --platform fanqie --json",
            "mcp_tool": "auth_login(platform='fanqie')",
        },
        {
            "step": 2,
            "action": "write_chapters",
            "description": "确认有已完成的章节（chapters/*.md）",
            "cli": "检查 chapters/ 目录",
            "mcp_tool": "—",
        },
        {
            "step": 3,
            "action": "publish_upload",
            "description": "上传全部章节到番茄小说",
            "cli": "novel-suite novel publish upload --platform fanqie --project <path> --json",
            "mcp_tool": "novel_publish_upload(platform='fanqie', project='<path>')",
        },
    ],
    "qidian": [
        {
            "step": 1,
            "action": "auth.login",
            "description": "登录起点作家专区",
            "cli": "novel-suite auth login --platform qidian --json",
            "mcp_tool": "auth.login",
        },
        {
            "step": 2,
            "action": "novel.export",
            "description": "导出小说章节",
            "cli": "novel-suite writer export --project <path> --format markdown --json",
            "mcp_tool": None,
        },
        {
            "step": 3,
            "action": "publish.upload",
            "description": "发布到起点（Phase C）",
            "cli": "novel-suite novel publish upload --project <path> --platform qidian --json",
            "mcp_tool": "publish.upload",
        },
    ],
    "analytics": [
        {
            "step": 1,
            "action": "record_data",
            "description": "发布后隔天录入播放量/收入数据",
            "cli": "novel-suite analytics record --project <path> --metrics 播放量=X 收入=Y --json",
            "mcp_tool": "analytics_record(project='<path>', metrics_json='{\"play_count\": X, \"revenue_yuan\": Y}')",
        },
        {
            "step": 2,
            "action": "view_report",
            "description": "查看项目效果报告",
            "cli": "novel-suite analytics report --project <path> --json",
            "mcp_tool": "analytics_report(project='<path>')",
        },
        {
            "step": 3,
            "action": "cross_report",
            "description": "查看所有项目的汇总对比",
            "cli": "novel-suite analytics cross-report --json",
            "mcp_tool": "analytics_report(project='')",
        },
    ],
    "jinjiang": [
        {
            "step": 1,
            "action": "auth.login",
            "description": "登录晋江作者后台",
            "cli": "novel-suite auth login --platform jinjiang --json",
            "mcp_tool": "auth.login",
        },
        {
            "step": 2,
            "action": "novel.export",
            "description": "导出小说章节",
            "cli": "novel-suite writer export --project <path> --format markdown --json",
            "mcp_tool": None,
        },
        {
            "step": 3,
            "action": "publish.upload",
            "description": "发布到晋江（Phase C）",
            "cli": "novel-suite novel publish upload --project <path> --platform jinjiang --json",
            "mcp_tool": "publish.upload",
        },
    ],
}


def get_publish_guide(platform: str) -> dict[str, Any]:
    """Return ordered publish steps for a platform."""
    key = platform.strip().lower()
    if key == "analytics":
        return {
            "platform": key,
            "platform_name": "数据追踪",
            "platform_type": "analytics",
            "step_count": len(GUIDE_STEPS.get(key, [])),
            "steps": GUIDE_STEPS.get(key, []),
        }
    if not validate_platform(key):
        return {
            "platform": key,
            "error": f"Unknown platform: {platform}",
            "steps": [],
        }
    info = get_platform(key) or {}
    return {
        "platform": key,
        "platform_name": info.get("name", key),
        "platform_type": info.get("type"),
        "step_count": len(GUIDE_STEPS.get(key, [])),
        "steps": GUIDE_STEPS.get(key, []),
    }


def list_publish_guides() -> list[dict[str, Any]]:
    return [get_publish_guide(key) for key in list_platform_keys()]
