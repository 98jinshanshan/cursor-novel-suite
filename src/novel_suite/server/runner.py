"""Server validate and stdlib HTTP runner."""

from __future__ import annotations

import importlib
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from novel_suite.core.agent_entry_menu import agent_entry_menu_root, validate_agent_entry_menu
from novel_suite.core.contracts import novel_suite_root
from novel_suite.core.errors import SERVER_RUN_OK, SERVER_VALIDATE_FAIL, SERVER_VALIDATE_OK
from novel_suite.core.paths import suite_root
from novel_suite.core.result import error_result, ok_result, Result
from novel_suite.server import app as api_app
from novel_suite.server.contracts import (
    CONTRACT_REL,
    REQUIRED_ROUTES,
    WORKBENCH_STATIC,
    api_contract_path,
    commercial_blocked_unchanged,
    contract_routes,
    workbench_root,
)
from novel_suite.writer import doctor, registry
from novel_suite.writer.intel import run_scan
from novel_suite.core.ip_production_demo import run_ip_production_demo
from novel_suite.core.novel_review_demo import run_novel_review_demo


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def validate_server_package() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    ns = novel_suite_root()

    for mod in (
        "novel_suite.server",
        "novel_suite.server.app",
        "novel_suite.server.contracts",
        "novel_suite.server.runner",
    ):
        try:
            importlib.import_module(mod)
            ok = True
            err = None
        except Exception as exc:  # noqa: BLE001
            ok = False
            err = str(exc)
        checks.append({"name": f"server.import.{mod}", "ok": ok, "path": mod, "details": [err] if err else []})

    contract = api_contract_path()
    checks.append(
        {
            "name": "server.api_contract_file",
            "ok": contract.is_file(),
            "path": _rel(root, contract),
        }
    )

    if contract.is_file():
        try:
            data = json.loads(contract.read_text(encoding="utf-8"))
            route_set = {(r.get("method"), r.get("path")) for r in data.get("routes", [])}
            missing = [f"{m} {p}" for m, p in REQUIRED_ROUTES if (m, p) not in route_set]
            checks.append(
                {
                    "name": "server.api_contract_routes",
                    "ok": not missing,
                    "path": _rel(root, contract),
                    "details": missing,
                }
            )
        except json.JSONDecodeError as exc:
            checks.append(
                {
                    "name": "server.api_contract_json",
                    "ok": False,
                    "path": _rel(root, contract),
                    "details": [str(exc)],
                }
            )

    checks.append(
        {
            "name": "server.commercial_blocked",
            "ok": commercial_blocked_unchanged(),
            "path": _rel(root, contract),
        }
    )

    menu_checks = validate_agent_entry_menu()
    failed_menu = [c for c in menu_checks if not c.get("ok")]
    checks.append(
        {
            "name": "server.agent_entry_menu",
            "ok": not failed_menu,
            "path": _rel(root, agent_entry_menu_root()),
        }
    )

    wb_static = ns / WORKBENCH_STATIC
    checks.append(
        {
            "name": "server.workbench_static",
            "ok": wb_static.is_file(),
            "path": _rel(root, wb_static),
        }
    )

    runners = (
        ("doctor", lambda: doctor.run_doctor()),
        ("writer_list", lambda: registry.load_registry()),
        ("writer_active", lambda: registry.get_active_slug()),
        ("scan_demo", lambda: run_scan(demo=True)),
        ("ip_demo", lambda: run_ip_production_demo()),
        ("novel_review_demo", lambda: run_novel_review_demo()),
    )
    for name, fn in runners:
        try:
            fn()
            ok = True
            detail = []
        except Exception as exc:  # noqa: BLE001
            ok = False
            detail = [str(exc)]
        checks.append({"name": f"server.runner.{name}", "ok": ok, "path": name, "details": detail})

    return checks


def run_server_validate() -> Result:
    checks = validate_server_package()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            SERVER_VALIDATE_FAIL,
            f"Server validate: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
            verdict="blocked",
        )
    return ok_result(
        SERVER_VALIDATE_OK,
        "Server package validation passed (contract + runners; commercial blocked)",
        checks=checks,
        route_count=len(contract_routes()),
        commercial_release_allowed=False,
        verdict="blocked",
        next_actions=[
            "novel-suite server run --host 127.0.0.1 --port 8765",
            f"Open {WORKBENCH_STATIC}",
        ],
    )


class _ApiHandler(BaseHTTPRequestHandler):
    server_version = "NovelSuiteUI/0.1"

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_static(self, rel_path: str) -> None:
        base = workbench_root() / "static"
        target = (base / rel_path).resolve()
        try:
            target.relative_to(base.resolve())
        except ValueError:
            self._send_json(403, api_app.result_to_api_payload(error_result("FORBIDDEN", "Path outside static")))
            return
        if not target.is_file():
            self._send_json(404, api_app.result_to_api_payload(error_result("NOT_FOUND", rel_path)))
            return
        content_type = "text/plain"
        if target.suffix == ".html":
            content_type = "text/html; charset=utf-8"
        elif target.suffix == ".css":
            content_type = "text/css; charset=utf-8"
        elif target.suffix == ".js":
            content_type = "application/javascript; charset=utf-8"
        data = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/workbench", "/workbench/"):
            self._send_static("index.html")
            return
        if parsed.path.startswith("/workbench/static/"):
            self._send_static(parsed.path.removeprefix("/workbench/static/"))
            return
        if parsed.path.startswith("/static/"):
            self._send_static(parsed.path.removeprefix("/static/"))
            return
        query = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        status, payload = api_app.dispatch("GET", parsed.path, query=query)
        self._send_json(status, payload)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else None
        status, payload = api_app.dispatch("POST", parsed.path, body=body)
        self._send_json(status, payload)


def run_server(*, host: str = "127.0.0.1", port: int = 8765) -> Result:
    """Non-blocking start (tests); prefer run_server_blocking for CLI."""
    validate = run_server_validate()
    if validate.status != "ok":
        return validate

    httpd = ThreadingHTTPServer((host, port), _ApiHandler)

    def _serve() -> None:
        httpd.serve_forever(poll_interval=0.5)

    thread = threading.Thread(target=_serve, name="novel-suite-server", daemon=True)
    thread.start()
    wb = workbench_root() / "static" / "index.html"
    return ok_result(
        SERVER_RUN_OK,
        f"Server listening on http://{host}:{port}",
        artifacts=[
            {"type": "url", "path": f"http://{host}:{port}/workbench"},
            {"type": "file", "path": str(wb)},
        ],
        host=host,
        port=port,
        commercial_release_allowed=False,
        verdict="blocked",
        next_actions=[f"Open http://{host}:{port}/workbench in browser"],
    )


def run_server_blocking(*, host: str = "127.0.0.1", port: int = 8765, json_out: bool = False) -> int:
    """Block until KeyboardInterrupt — used by CLI server run."""
    from novel_suite.core.result import emit

    validate = run_server_validate()
    if validate.status != "ok":
        return emit(validate, json_out=json_out)

    httpd = ThreadingHTTPServer((host, port), _ApiHandler)
    start = ok_result(
        SERVER_RUN_OK,
        f"Server listening on http://{host}:{port}",
        artifacts=[{"type": "url", "path": f"http://{host}:{port}/workbench"}],
        host=host,
        port=port,
        commercial_release_allowed=False,
        verdict="blocked",
    )
    if json_out:
        emit(start, json_out=True)
    else:
        print(f"Novel Suite UI server: http://{host}:{port}/workbench (Ctrl+C to stop)")
    try:
        httpd.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        httpd.shutdown()
    return 0
