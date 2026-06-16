"""Tests for OAuth callback server (Sprint 4 Phase A)."""

from __future__ import annotations

import socket
import threading
import time
from urllib.parse import urlencode
from urllib.request import urlopen

from novel_suite.auth.server import find_callback_port, get_redirect_uri, start_callback_server


def test_get_redirect_uri():
    assert get_redirect_uri(9876) == "http://127.0.0.1:9876/callback"


def test_find_callback_port():
    port = find_callback_port(start=19876, attempts=3)
    assert port >= 19876


def test_callback_server_receives_code():
    port = find_callback_port(start=19880, attempts=10)
    redirect = get_redirect_uri(port)

    def _hit_callback() -> None:
        time.sleep(0.2)
        query = urlencode({"code": "test_auth_code_123"})
        urlopen(f"http://127.0.0.1:{port}/callback?{query}", timeout=5)

    thread = threading.Thread(target=_hit_callback, daemon=True)
    thread.start()
    code = start_callback_server(port=port, timeout_sec=5.0)
    thread.join(timeout=5)
    assert code == "test_auth_code_123"


def test_callback_server_error():
    port = find_callback_port(start=19900, attempts=10)

    def _hit_error() -> None:
        time.sleep(0.2)
        query = urlencode({"error": "access_denied"})
        urlopen(f"http://127.0.0.1:{port}/callback?{query}", timeout=5)

    thread = threading.Thread(target=_hit_error, daemon=True)
    thread.start()
    code = start_callback_server(port=port, timeout_sec=5.0)
    thread.join(timeout=5)
    assert code is None
