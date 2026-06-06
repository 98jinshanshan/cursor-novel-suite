"""Environment variable accessors — no hardcoded secrets (Sprint 0 Day 1)."""

from __future__ import annotations

import os

_LOCALHOST = "127.0.0.1"


def getenv(name: str, default: str = "") -> str:
    """Read env var; never embed real credentials as defaults."""
    return (os.environ.get(name) or default).strip()


def get_qdrant_url() -> str:
    """Explicit QDRANT_URL only — empty means file-only memory mode."""
    return getenv("QDRANT_URL")


def get_qdrant_url_or_default() -> str:
    return get_qdrant_url() or f"http://{_LOCALHOST}:6333"


def get_qdrant_api_key() -> str:
    return getenv("QDRANT_API_KEY")


def get_memory_embed_backend() -> str:
    raw = getenv("MEMORY_EMBED_BACKEND", "hash").lower()
    return raw if raw in ("hash", "m3e") else "hash"


def get_memory_embed_model() -> str:
    return getenv("MEMORY_EMBED_MODEL", "moka-ai/m3e-base")


def get_ollama_host() -> str:
    return getenv("OLLAMA_HOST", f"http://{_LOCALHOST}:11434")


def get_comfyui_url() -> str:
    return getenv("COMFYUI_URL", f"http://{_LOCALHOST}:8000")


def get_openai_api_key() -> str:
    return getenv("OPENAI_API_KEY")


def get_deepseek_api_key() -> str:
    return getenv("DEEPSEEK_API_KEY")


def allow_skip_gate() -> bool:
    return getenv("NOVEL_SUITE_ALLOW_SKIP_GATE", "0") in ("1", "true", "yes")
