"""Platform registry — definitions, capabilities, and auth types."""

from __future__ import annotations

from typing import Any, Literal

PlatformType = Literal["video", "novel"]

PLATFORM_REGISTRY: dict[str, dict[str, Any]] = {
    "douyin": {
        "type": "video",
        "name": "抖音",
        "aspect": "9:16",
        "max_duration_sec": 180,
        "content_type": "novel_summary",
        "auth_type": "oauth2_cookie",
        "creator_url": "https://creator.douyin.com/",
        "upload_api": "https://creator.douyin.com/creator-micro/content/upload",
        "icon": "🎵",
        "default_voice": "zh-CN-XiaoxiaoNeural",
    },
    "kuaishou": {
        "type": "video",
        "name": "快手",
        "aspect": "9:16",
        "max_duration_sec": 120,
        "content_type": "novel_summary",
        "auth_type": "oauth2_cookie",
        "creator_url": "https://cp.kuaishou.com/",
        "upload_api": "https://cp.kuaishou.com/article/publish/video",
        "icon": "📹",
        "default_voice": "zh-CN-XiaoxiaoNeural",
    },
    "bilibili": {
        "type": "video",
        "name": "B站",
        "aspect": "16:9",
        "max_duration_sec": 600,
        "content_type": "novel_summary",
        "auth_type": "oauth2_cookie",
        "creator_url": "https://member.bilibili.com/",
        "upload_api": "https://member.bilibili.com/platform/upload/video",
        "icon": "📺",
        "default_voice": "zh-CN-XiaoxiaoNeural",
    },
    "fanqie": {
        "type": "novel",
        "name": "番茄小说",
        "content_type": "web_novel",
        "auth_type": "api_key",
        "api_base": "https://open.fanqienovel.com/",
        "chapter_format": "markdown",
        "chapter_word_limit": 3000,
        "icon": "🍅",
    },
    "qidian": {
        "type": "novel",
        "name": "起点中文网",
        "content_type": "web_novel",
        "auth_type": "oauth2_cookie",
        "creator_url": "https://write.qidian.com/",
        "chapter_format": "markdown",
        "chapter_word_limit": 2500,
        "icon": "📖",
    },
    "jinjiang": {
        "type": "novel",
        "name": "晋江文学城",
        "content_type": "web_novel",
        "auth_type": "oauth2_cookie",
        "creator_url": "https://www.jjwxc.net/mywork.php",
        "chapter_format": "markdown",
        "chapter_word_limit": 3000,
        "icon": "🌸",
    },
}


def list_platform_keys(*, platform_type: PlatformType | None = None) -> list[str]:
    if platform_type is None:
        return sorted(PLATFORM_REGISTRY.keys())
    return sorted(k for k, v in PLATFORM_REGISTRY.items() if v.get("type") == platform_type)


def list_platforms(*, platform_type: PlatformType | None = None) -> list[dict[str, Any]]:
    keys = list_platform_keys(platform_type=platform_type)
    return [{"key": key, **PLATFORM_REGISTRY[key]} for key in keys]


def get_platform(key: str) -> dict[str, Any] | None:
    entry = PLATFORM_REGISTRY.get(key.strip().lower())
    if entry is None:
        return None
    return {"key": key.strip().lower(), **entry}


def validate_platform(key: str) -> bool:
    return key.strip().lower() in PLATFORM_REGISTRY
