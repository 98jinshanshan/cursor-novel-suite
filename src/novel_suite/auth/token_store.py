"""Token encryption and persistent storage (stdlib envelope encryption)."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from novel_suite.core.env_config import getenv

TOKEN_MAX_AGE_DAYS = 7
_ENVELOPE_VERSION = 1


def tokens_dir() -> Path:
    override = getenv("NOVEL_SUITE_TOKEN_DIR")
    base = Path(override) if override else Path.home() / ".novel-suite" / "tokens"
    base.mkdir(parents=True, exist_ok=True)
    try:
        base.chmod(stat.S_IRWXU)
    except (OSError, NotImplementedError):
        pass
    return base


def _token_path(platform: str) -> Path:
    return tokens_dir() / f"{platform.strip().lower()}.json"


def _derive_key() -> bytes:
    secret = getenv("NOVEL_SUITE_TOKEN_KEY") or str(Path.home())
    return hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"), b"novel-suite-token-v1", 100_000, dklen=32)


def _xor_stream(data: bytes, key: bytes, nonce: bytes) -> bytes:
    out = bytearray()
    counter = 0
    while len(out) < len(data):
        block = hmac.new(key, nonce + counter.to_bytes(4, "big"), hashlib.sha256).digest()
        out.extend(block)
        counter += 1
    stream = bytes(out[: len(data)])
    return bytes(a ^ b for a, b in zip(data, stream, strict=True))


def _encrypt_payload(payload: dict[str, Any]) -> dict[str, Any]:
    key = _derive_key()
    nonce = os.urandom(16)
    plaintext = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    ciphertext = _xor_stream(plaintext, key, nonce)
    tag = hmac.new(key, nonce + ciphertext, hashlib.sha256).hexdigest()
    return {
        "v": _ENVELOPE_VERSION,
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
        "tag": tag,
    }


def _decrypt_payload(envelope: dict[str, Any]) -> dict[str, Any] | None:
    if envelope.get("v") != _ENVELOPE_VERSION:
        return None
    try:
        key = _derive_key()
        nonce = base64.b64decode(str(envelope["nonce"]))
        ciphertext = base64.b64decode(str(envelope["ciphertext"]))
        tag = str(envelope.get("tag", ""))
        expected = hmac.new(key, nonce + ciphertext, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(tag, expected):
            return None
        plaintext = _xor_stream(ciphertext, key, nonce)
        data = json.loads(plaintext.decode("utf-8"))
        return data if isinstance(data, dict) else None
    except (KeyError, ValueError, json.JSONDecodeError, OSError):
        return None


def save_token(platform: str, token_data: dict[str, Any]) -> Path:
    """Encrypt and persist platform token data."""
    path = _token_path(platform)
    envelope = _encrypt_payload(
        {
            "platform": platform.strip().lower(),
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "token": token_data,
        }
    )
    path.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except (OSError, NotImplementedError):
        pass
    return path


def load_token(platform: str) -> dict[str, Any] | None:
    """Load decrypted token data; None when missing, corrupt, or expired."""
    path = _token_path(platform)
    if not path.is_file():
        return None
    try:
        envelope = json.loads(path.read_text(encoding="utf-8"))
        payload = _decrypt_payload(envelope)
        if payload is None:
            return None
        saved_at = payload.get("saved_at", "")
        if saved_at:
            try:
                dt = datetime.fromisoformat(saved_at)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                if (datetime.now(timezone.utc) - dt).days > TOKEN_MAX_AGE_DAYS:
                    return None
            except (ValueError, TypeError):
                return None
        token = payload.get("token")
        return token if isinstance(token, dict) else None
    except (json.JSONDecodeError, OSError):
        return None


def delete_token(platform: str) -> None:
    path = _token_path(platform)
    if path.is_file():
        path.unlink()


def token_status(platform: str) -> dict[str, Any]:
    """Return auth status for one platform."""
    path = _token_path(platform)
    token = load_token(platform)
    if token is None:
        reason = "not_found_or_expired" if not path.is_file() else "expired_or_invalid"
        return {
            "platform": platform,
            "valid": False,
            "reason": reason,
            "file": str(path) if path.is_file() else None,
        }
    expires_at = token.get("expires_at")
    return {
        "platform": platform,
        "valid": True,
        "auth_type": token.get("auth_type"),
        "expires_at": expires_at,
        "file": str(path),
        "file_size": path.stat().st_size,
    }


def all_token_statuses() -> list[dict[str, Any]]:
    from novel_suite.platforms._registry import list_platform_keys

    return [token_status(key) for key in list_platform_keys()]
