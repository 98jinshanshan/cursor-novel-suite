"""API route handlers — return Result Contract dicts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from novel_suite.core import errors as E
from novel_suite.core.paths import intel_dir, suite_root
from novel_suite.core.result import error_result, ok_result, Result
from novel_suite.writer import doctor, registry
from novel_suite.writer.intel import run_scan
from novel_suite.core.ip_production_demo import run_ip_production_demo
from novel_suite.core.novel_review_demo import run_novel_review_demo

_EVENT_LOG: list[dict[str, Any]] = []


def _record_event(kind: str, *, code: str, message: str) -> None:
    _EVENT_LOG.append(
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "kind": kind,
            "code": code,
            "message": message,
        }
    )
    if len(_EVENT_LOG) > 50:
        del _EVENT_LOG[:-50]


def result_to_api_payload(result: Result) -> dict[str, Any]:
    data = result.to_dict()
    details = data.pop("details", {}) or {}
    payload: dict[str, Any] = {
        "status": data.get("status", "error"),
        "code": data.get("code", ""),
        "message": data.get("message", ""),
        "artifacts": data.get("artifacts", []),
        "next_actions": data.get("next_actions", []),
        "required": data.get("required", []),
        "job": details.pop("job", {}) if isinstance(details.get("job"), dict) else {},
        "blocker": details.pop("blocker", details.pop("blockers", details.pop("run_blockers", []))),
        "commercial_release_allowed": details.pop("commercial_release_allowed", False),
        "verdict": details.pop("verdict", "blocked"),
    }
    if details:
        payload["details"] = details
    return payload


def handle_doctor() -> dict[str, Any]:
    result = doctor.run_doctor()
    _record_event("doctor", code=result.code, message=result.message)
    out = result_to_api_payload(result)
    out.setdefault("commercial_release_allowed", False)
    out.setdefault("verdict", "blocked")
    return out


def handle_projects_list() -> dict[str, Any]:
    reg = registry.load_registry()
    novels = reg.get("novels", [])
    result = ok_result(
        "LIST_OK",
        f"{len(novels)} novel(s) registered",
        novels=novels,
        active_slug=registry.get_active_slug(),
        commercial_release_allowed=False,
        verdict="blocked",
    )
    return result_to_api_payload(result)


def handle_projects_active() -> dict[str, Any]:
    slug = registry.get_active_slug()
    if not slug:
        result = error_result(
            "NO_ACTIVE_NOVEL",
            "No active novel",
            next_actions=["novel-suite writer use <slug>"],
            commercial_release_allowed=False,
            verdict="blocked",
        )
        return result_to_api_payload(result)
    path = registry.find_by_slug(slug)
    if path is None:
        result = error_result(
            "STALE_ACTIVE_SLUG",
            f"Active slug not in registry: {slug}",
            slug=slug,
            stale=True,
            next_actions=[
                "novel-suite writer list --json",
                "novel-suite writer use <valid-slug> --json",
            ],
            commercial_release_allowed=False,
            verdict="blocked",
        )
        return result_to_api_payload(result)
    result = ok_result(
        "ACTIVE_OK",
        f"Active novel: {slug}",
        artifacts=[{"type": "directory", "path": str(path)}] if path else [],
        slug=slug,
        commercial_release_allowed=False,
        verdict="blocked",
    )
    return result_to_api_payload(result)


def handle_projects_use(body: dict[str, Any] | None) -> dict[str, Any]:
    slug = (body or {}).get("slug", "").strip()
    if not slug:
        return result_to_api_payload(
            error_result("MISSING_SLUG", "POST body requires slug", commercial_release_allowed=False)
        )
    try:
        path = registry.set_active(slug)
    except ValueError as exc:
        return result_to_api_payload(
            error_result("UNKNOWN_NOVEL_SLUG", str(exc), commercial_release_allowed=False)
        )
    _record_event("project_use", code="USE_OK", message=f"Active set to {slug}")
    return result_to_api_payload(
        ok_result(
            "USE_OK",
            f"Active novel set to {slug}",
            artifacts=[{"type": "directory", "path": str(path)}],
            slug=slug,
            commercial_release_allowed=False,
            verdict="blocked",
        )
    )


def handle_project_status(slug: str) -> dict[str, Any]:
    path = registry.find_by_slug(slug)
    if path is None:
        return result_to_api_payload(
            error_result("UNKNOWN_NOVEL_SLUG", f"Unknown slug: {slug}", commercial_release_allowed=False)
        )
    story = path / "story.md"
    title = ""
    if story.is_file():
        for line in story.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
    return result_to_api_payload(
        ok_result(
            "STATUS_OK",
            title or slug,
            artifacts=[{"type": "directory", "path": str(path)}],
            slug=slug,
            title=title,
            commercial_release_allowed=False,
            verdict="blocked",
        )
    )


def handle_market_scan_run(body: dict[str, Any] | None) -> dict[str, Any]:
    """Demo-only market scan — never live/network."""
    payload = body or {}
    if payload.get("live") or payload.get("demo") is False:
        return result_to_api_payload(
            error_result(
                E.SCAN_LIVE_BLOCKED,
                "Market scan API allows demo only; live scan blocked",
                next_actions=["Use demo:true or omit body"],
                commercial_release_allowed=False,
                verdict="blocked",
                blocker=["live_scan_blocked"],
            )
        )
    result = run_scan(demo=True)
    _record_event("market_scan", code=result.code, message=result.message)
    out = result_to_api_payload(result)
    out["demo_only"] = True
    out["commercial_release_allowed"] = False
    out["verdict"] = "blocked"
    return out


def handle_ip_to_short_drama_run(body: dict[str, Any] | None) -> dict[str, Any]:
    """Offline ip.to_short_drama demo — no video/adapter."""
    payload = body or {}
    if payload.get("live") or payload.get("adapter") is True:
        return result_to_api_payload(
            error_result(
                "ADAPTER_BLOCKED",
                "IP to short drama API allows offline demo only",
                commercial_release_allowed=False,
                verdict="blocked",
                adapter_enabled=False,
                external_call_performed=False,
                blocker=["adapter_disabled"],
            )
        )
    result = run_ip_production_demo()
    _record_event("ip_to_short_drama", code=result.code, message=result.message)
    out = result_to_api_payload(result)
    out["demo_only"] = True
    out["adapter_enabled"] = False
    out["external_call_performed"] = False
    out["commercial_release_allowed"] = False
    out["verdict"] = "blocked"
    return out


def handle_novel_review_run(body: dict[str, Any] | None) -> dict[str, Any]:
    """Offline novel.review demo — suggestions only, no project write."""
    payload = body or {}
    if payload.get("auto_rewrite") or payload.get("write_project"):
        return result_to_api_payload(
            error_result(
                "AUTO_REWRITE_BLOCKED",
                "Novel review demo does not auto-rewrite or write projects",
                commercial_release_allowed=False,
                verdict="blocked",
                run_blockers=["auto_rewrite_blocked"],
            )
        )
    result = run_novel_review_demo()
    _record_event("novel_review", code=result.code, message=result.message)
    out = result_to_api_payload(result)
    out["demo_only"] = True
    out["auto_rewrite_allowed"] = False
    out["adapter_enabled"] = False
    out["external_call_performed"] = False
    out["commercial_release_allowed"] = False
    out["verdict"] = "blocked"
    return out


def handle_realgen_run(body: dict[str, Any] | None) -> dict[str, Any]:
    """RealGen-1 已废止 — 重定向 RealPipeline-2B NVP 证据链。"""
    result = error_result(
        "REALGEN_DEMO_DEPRECATED",
        "RealGen-1 旁路已废止；请使用 realpipeline --project novels/novel-837dd4f1",
        commercial_release_allowed=False,
        verdict="blocked",
        next_actions=[
            "novel-suite realpipeline validate --project novels/novel-837dd4f1 --json",
            "Open novels/novel-837dd4f1/reports/realpipeline_2b_summary.md",
        ],
    )
    _record_event("realgen", code=result.code, message=result.message)
    return result_to_api_payload(result)


def _intel_artifacts(project_slug: str | None) -> list[dict[str, Any]]:
    root = intel_dir()
    items: list[dict[str, Any]] = []
    for sub in ("radar", "concepts"):
        d = root / sub
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.json"))[:20]:
            items.append({"type": "file", "path": str(p), "label": sub, "project": project_slug})
    fixture = suite_root() / "intel" / "fixtures" / "smoke-hits.json"
    if fixture.is_file():
        items.append({"type": "file", "path": str(fixture), "label": "demo_fixture"})
    return items


def handle_artifacts(query: dict[str, str]) -> dict[str, Any]:
    project = query.get("project", "").strip() or None
    arts = _intel_artifacts(project)
    return result_to_api_payload(
        ok_result(
            "ARTIFACTS_OK",
            f"{len(arts)} artifact(s)",
            artifacts=arts,
            project=project,
            commercial_release_allowed=False,
            verdict="blocked",
        )
    )


def handle_events() -> dict[str, Any]:
    heartbeat = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "type": "heartbeat",
        "commercial_release_allowed": False,
        "verdict": "blocked",
    }
    return result_to_api_payload(
        ok_result(
            "EVENTS_OK",
            "Recent server events",
            events=[heartbeat, *_EVENT_LOG[-10:]],
            commercial_release_allowed=False,
            verdict="blocked",
        )
    )


def dispatch(method: str, path: str, *, body: bytes | None = None, query: dict[str, str] | None = None) -> tuple[int, dict[str, Any]]:
    """Route HTTP request to handler; returns (status_code, json_body)."""
    method = method.upper()
    query = query or {}
    parsed: dict[str, Any] | None = None
    if body:
        try:
            parsed = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            return 400, result_to_api_payload(error_result("INVALID_JSON", "Request body must be JSON"))

    if method == "GET" and path == "/api/doctor":
        return 200, handle_doctor()
    if method == "GET" and path == "/api/projects":
        return 200, handle_projects_list()
    if method == "GET" and path == "/api/projects/active":
        return 200, handle_projects_active()
    if method == "POST" and path == "/api/projects/use":
        return 200, handle_projects_use(parsed)
    if method == "POST" and path == "/api/agents/market-scan/run":
        return 200, handle_market_scan_run(parsed)
    if method == "POST" and path == "/api/agents/ip-to-short-drama/run":
        return 200, handle_ip_to_short_drama_run(parsed)
    if method == "POST" and path == "/api/agents/novel-review/run":
        return 200, handle_novel_review_run(parsed)
    if method == "POST" and path == "/api/agents/realgen/run":
        return 200, handle_realgen_run(parsed)
    if method == "GET" and path == "/api/events":
        return 200, handle_events()
    if method == "GET" and path == "/api/artifacts":
        return 200, handle_artifacts(query)
    if method == "GET" and path.startswith("/api/projects/") and path.endswith("/status"):
        slug = path.removeprefix("/api/projects/").removesuffix("/status").strip("/")
        if slug:
            return 200, handle_project_status(slug)

    return 404, result_to_api_payload(error_result("NOT_FOUND", f"No route for {method} {path}"))
