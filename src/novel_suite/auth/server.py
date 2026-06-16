"""Local OAuth callback server — listens on localhost for platform redirects."""

from __future__ import annotations

import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable
from urllib.parse import parse_qs, urlparse

CALLBACK_PORT = 9876
CALLBACK_HOST = "127.0.0.1"


class _CallbackState:
    auth_code: str | None = None
    error: str | None = None


class CallbackHandler(BaseHTTPRequestHandler):
    state: _CallbackState = _CallbackState()

    def do_GET(self) -> None:
        params = parse_qs(urlparse(self.path).query)
        if "code" in params:
            CallbackHandler.state.auth_code = params["code"][0]
            self._respond_html("登录成功！请关闭此页面返回终端。")
        elif "error" in params:
            CallbackHandler.state.error = params["error"][0]
            self._respond_html(f"登录失败：{params['error'][0]}。请关闭此页面返回终端。")
        else:
            self._respond_html("等待认证...")

    def _respond_html(self, message: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        body = f"<html><body><h2>{message}</h2></body></html>"
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, format: str, *args: object) -> None:
        return


def get_redirect_uri(port: int = CALLBACK_PORT) -> str:
    return f"http://{CALLBACK_HOST}:{port}/callback"


def _port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def start_callback_server(
    *,
    timeout_sec: float = 300.0,
    port: int = CALLBACK_PORT,
    on_ready: Callable[[str], None] | None = None,
) -> str | None:
    """Start callback server and wait for OAuth authorization code."""
    CallbackHandler.state = _CallbackState()
    server = HTTPServer((CALLBACK_HOST, port), CallbackHandler)
    server.timeout = 1.0
    deadline = timeout_sec
    if on_ready:
        on_ready(get_redirect_uri(port))

    def _serve() -> None:
        while CallbackHandler.state.auth_code is None and CallbackHandler.state.error is None:
            server.handle_request()

    thread = threading.Thread(target=_serve, daemon=True)
    thread.start()
    thread.join(timeout=deadline)
    server.server_close()

    if CallbackHandler.state.error:
        return None
    return CallbackHandler.state.auth_code


def find_callback_port(start: int = CALLBACK_PORT, attempts: int = 5) -> int:
    for offset in range(attempts):
        port = start + offset
        if _port_available(CALLBACK_HOST, port):
            return port
    return start
