"""Analytics metric schema and validation."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

METRIC_KEYS = frozenset(
    {
        "play_count",
        "like_count",
        "comment_count",
        "share_count",
        "revenue_yuan",
        "completion_rate",
        "follower_gain",
    }
)

SUM_METRICS = frozenset(
    {
        "play_count",
        "like_count",
        "comment_count",
        "share_count",
        "revenue_yuan",
        "follower_gain",
    }
)

AVG_METRICS = frozenset({"completion_rate"})

METRIC_ALIASES: dict[str, str] = {
    "播放量": "play_count",
    "播放": "play_count",
    "play_count": "play_count",
    "plays": "play_count",
    "点赞": "like_count",
    "点赞数": "like_count",
    "like_count": "like_count",
    "likes": "like_count",
    "评论": "comment_count",
    "评论数": "comment_count",
    "comment_count": "comment_count",
    "comments": "comment_count",
    "分享": "share_count",
    "分享数": "share_count",
    "share_count": "share_count",
    "shares": "share_count",
    "收入": "revenue_yuan",
    "收益": "revenue_yuan",
    "revenue": "revenue_yuan",
    "revenue_yuan": "revenue_yuan",
    "完读率": "completion_rate",
    "completion_rate": "completion_rate",
    "completion": "completion_rate",
    "涨粉": "follower_gain",
    "follower_gain": "follower_gain",
    "followers": "follower_gain",
}


def normalize_metric_key(raw_key: str) -> str | None:
    key = raw_key.strip()
    if not key:
        return None
    return METRIC_ALIASES.get(key) or METRIC_ALIASES.get(key.lower()) or (
        key if key in METRIC_KEYS else None
    )


def validate_metrics(metrics: dict[str, Any]) -> tuple[bool, list[str]]:
    """Return (ok, errors)."""
    if not metrics:
        return False, ["no metrics provided"]
    errors: list[str] = []
    for key, value in metrics.items():
        if key not in METRIC_KEYS:
            errors.append(f"unknown metric: {key}")
            continue
        try:
            float(value)
        except (TypeError, ValueError):
            errors.append(f"invalid value for {key}: {value!r}")
    return (len(errors) == 0, errors)


def parse_metrics_text(metrics_text: str) -> tuple[dict[str, float], list[str]]:
    """Parse ``播放量=15000 收入=12.5`` style input."""
    metrics: dict[str, float] = {}
    errors: list[str] = []
    for token in metrics_text.split():
        if "=" not in token:
            errors.append(f"invalid token (expected key=value): {token}")
            continue
        raw_key, raw_value = token.split("=", 1)
        norm_key = normalize_metric_key(raw_key)
        if norm_key is None:
            errors.append(f"unknown metric key: {raw_key}")
            continue
        try:
            metrics[norm_key] = float(raw_value)
        except ValueError:
            errors.append(f"invalid value for {raw_key}: {raw_value!r}")
    return metrics, errors


def parse_metrics_json(metrics_json: dict[str, Any]) -> tuple[dict[str, float], list[str]]:
    metrics: dict[str, float] = {}
    errors: list[str] = []
    for raw_key, raw_value in metrics_json.items():
        norm_key = normalize_metric_key(str(raw_key))
        if norm_key is None:
            errors.append(f"unknown metric key: {raw_key}")
            continue
        try:
            metrics[norm_key] = float(raw_value)
        except (TypeError, ValueError):
            errors.append(f"invalid value for {raw_key}: {raw_value!r}")
    return metrics, errors


def create_analytics_record(
    *,
    content_type: str,
    content_key: str,
    metrics: dict[str, float],
    note: str = "",
) -> dict[str, Any]:
    return {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "content_type": content_type,
        "content_key": content_key,
        "metrics": metrics,
        "note": note,
    }
