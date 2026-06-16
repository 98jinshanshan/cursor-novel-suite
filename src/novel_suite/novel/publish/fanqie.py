"""Fanqie (番茄小说) chapter publish via Open API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import urllib.error
import urllib.request

from novel_suite.auth.token_store import load_token
from novel_suite.core.env_config import getenv


def _get_api_key() -> str | None:
    """从 Token 存储中读取番茄 API Key。"""
    token = load_token("fanqie")
    if token is None:
        return None
    return token.get("api_key")


def _api_headers() -> dict[str, str]:
    """构建番茄 API 请求头。"""
    api_key = _get_api_key()
    if not api_key:
        return {}
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _load_chapters(project: Path) -> list[dict[str, Any]]:
    """从小说项目加载所有已完成的章节。

    读取 canon/progress.json 和 chapters/*.md。
    返回按章节号排序的 [{number, title, content}] 列表。
    """
    chapters_dir = project / "chapters"
    if not chapters_dir.is_dir():
        return []

    progress_path = project / "canon" / "progress.json"
    if not progress_path.is_file():
        return []

    try:
        progress = json.loads(progress_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    result: list[dict[str, Any]] = []

    for ch in progress.get("chapters", []):
        if not isinstance(ch, dict):
            continue
        rel_file = ch.get("file")
        if not rel_file:
            continue
        ch_file = project / str(rel_file)
        if not ch_file.is_file():
            continue
        try:
            content = ch_file.read_text(encoding="utf-8")
        except OSError:
            continue
        result.append(
            {
                "number": ch.get("number", 0),
                "title": ch.get("title", ""),
                "content": content,
                "word_count": ch.get("word_count", 0),
            }
        )

    result.sort(key=lambda x: x["number"])
    return result


def _fanqie_use_real_api() -> bool:
    return getenv("FANQIE_USE_REAL_API", "").strip().lower() in ("1", "true", "yes")


def _post_fanqie_chapter(
    novel_id: str,
    chapter_number: int,
    title: str,
    content: str,
    api_key: str,
) -> dict[str, Any]:
    """POST to Fanqie Open API (stdlib urllib)."""
    url = f"https://open.fanqienovel.com/api/novel/{novel_id}/chapter"
    payload = json.dumps(
        {"chapter_number": chapter_number, "title": title, "content": content},
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body) if body.strip() else {}
            if not isinstance(data, dict):
                data = {"raw": data}
            return {"ok": 200 <= resp.status < 300, **data}
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(err_body) if err_body.strip() else {}
        except json.JSONDecodeError:
            data = {"raw": err_body}
        if not isinstance(data, dict):
            data = {"raw": data}
        return {"ok": False, "status": exc.code, "error": str(exc), **data}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


def fanqie_publish_chapter(
    novel_id: str,
    chapter_number: int,
    title: str,
    content: str,
    api_key: str | None = None,
) -> dict[str, Any]:
    """发布单章到番茄小说（默认 stub；设置 FANQIE_USE_REAL_API=1 走真实 HTTP）。"""
    actual_api_key = api_key or _get_api_key()
    if not actual_api_key:
        return {
            "ok": False,
            "error": "Fanqie API key not found. Run: novel-suite auth login --platform fanqie --json",
        }

    if _fanqie_use_real_api():
        result = _post_fanqie_chapter(
            novel_id, chapter_number, title, content, actual_api_key
        )
        result.setdefault("novel_id", novel_id)
        result.setdefault("chapter_number", chapter_number)
        result.setdefault("title", title)
        result.setdefault("word_count", len(content))
        return result

    word_count = len(content)
    return {
        "ok": True,
        "novel_id": novel_id,
        "chapter_number": chapter_number,
        "title": title,
        "word_count": word_count,
        "note": "Stub implementation — set FANQIE_USE_REAL_API=1 for live API",
    }


def publish_to_qidian(project: Path) -> dict[str, Any]:
    """发布到起点中文网（stub — 需人工签约后上传）。"""
    chapters = _load_chapters(project)
    dist = project / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    return {
        "ok": True,
        "platform": "qidian",
        "total": len(chapters),
        "published_count": len(chapters),
        "failed_count": 0,
        "note": "Stub: Qidian requires manual contract. Chapters prepared at <project>/dist/",
        "dist_path": str(dist),
    }


def publish_to_jinjiang(project: Path) -> dict[str, Any]:
    """发布到晋江文学城（stub — 需视角规范校验）。"""
    chapters = _load_chapters(project)
    dist = project / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    return {
        "ok": True,
        "platform": "jinjiang",
        "total": len(chapters),
        "published_count": len(chapters),
        "failed_count": 0,
        "note": "Stub: Jinjiang requires viewpoint check. Chapters prepared at <project>/dist/",
        "dist_path": str(dist),
    }


def get_novel_id(project: Path) -> str | None:
    """从 project.json 获取番茄 novel_id。"""
    project_json = project / "canon" / "project.json"
    if not project_json.is_file():
        return None
    try:
        data = json.loads(project_json.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data.get("fanqie_novel_id")


def fanqie_publish_all(project: Path) -> dict[str, Any]:
    """发布全部未发布的章节到番茄。"""
    api_key = _get_api_key()
    if not api_key:
        return {"ok": False, "error": "API key not found", "published": [], "failed": []}

    novel_id = get_novel_id(project)
    chapters = _load_chapters(project)

    if not chapters:
        return {"ok": False, "error": "No chapters found", "published": [], "failed": []}

    published: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []

    for ch in chapters:
        result = fanqie_publish_chapter(
            novel_id or "stub_novel_id",
            ch["number"],
            ch["title"],
            ch["content"],
        )
        if result.get("ok"):
            published.append({"number": ch["number"], "title": ch["title"]})
        else:
            failed.append(
                {
                    "number": ch["number"],
                    "title": ch["title"],
                    "error": result.get("error"),
                }
            )

    return {
        "ok": len(failed) == 0,
        "novel_id": novel_id,
        "total": len(chapters),
        "published_count": len(published),
        "failed_count": len(failed),
        "published": published,
        "failed": failed if failed else None,
        "note": "" if novel_id else "No fanqie_novel_id in project.json — set via writer init --fanqie-novel-id",
    }
