"""Path bounds, MCP roots, graphify token sanitization, safe HTTP downloads."""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from novel_suite.core import errors as E

_GRAPHIFY_TOKEN_MAX = 80
_GRAPHIFY_TOKEN_PATTERN = re.compile(
    r"^[\w\u4e00-\u9fff\u3400-\u4dbf·\-]{1,80}$",
    re.UNICODE,
)

# OpenAI image CDN hosts (extend when API adds regions)
_OPENAI_IMAGE_HOST_SUFFIXES = (
    "oaidalleapiprodscus.blob.core.windows.net",
    "oaidalleapiprod.blob.core.windows.net",
    "cdn.openai.com",
)

DOWNLOAD_MAX_BYTES = 20 * 1024 * 1024
DOWNLOAD_TIMEOUT_SEC = 30.0
INTEL_HTML_MAX_BYTES = 2 * 1024 * 1024


def sanitize_graphify_token(name: str, *, label: str = "identifier") -> str:
    """Reject CLI/meta injection in graphify path/query arguments."""
    s = (name or "").strip()
    if not s or len(s) > _GRAPHIFY_TOKEN_MAX:
        raise ValueError(
            f"Invalid graphify {label}: length must be 1..{_GRAPHIFY_TOKEN_MAX}"
        )
    if any(c in s for c in "\n\r\x00\t"):
        raise ValueError(f"Invalid graphify {label}: control characters forbidden")
    if s.startswith("-") or "--" in s:
        raise ValueError(f"Invalid graphify {label}: must not look like CLI flags")
    if not _GRAPHIFY_TOKEN_PATTERN.match(s):
        raise ValueError(
            f"Invalid graphify {label}: use letters, digits, CJK, underscore, hyphen, middle dot"
        )
    return s


def system_temp_roots() -> list[Path]:
    seen: set[str] = set()
    roots: list[Path] = []
    for key in ("TMPDIR", "TEMP", "TMP"):
        raw = os.environ.get(key, "").strip()
        if raw:
            p = Path(raw).expanduser().resolve()
            key_s = str(p)
            if key_s not in seen:
                seen.add(key_s)
                roots.append(p)
    default = Path(tempfile.gettempdir()).resolve()
    if str(default) not in seen:
        roots.append(default)
    return roots


def assert_chapter_input_path(project: Path, input_path: Path) -> Path:
    """Allow draft input under project or system temp (pytest / agent scratch)."""
    resolved = input_path.expanduser().resolve()
    root = project.resolve()
    try:
        resolved.relative_to(root)
        return resolved
    except ValueError:
        pass
    for base in system_temp_roots():
        try:
            resolved.relative_to(base)
            return resolved
        except ValueError:
            continue
    raise ValueError(
        f"{E.CHAPTER_INPUT_OUT_OF_BOUNDS}: --input must be under the novel project "
        f"or system temp ({root} rejected {resolved})"
    )


def mcp_allowed_roots() -> list[Path]:
    from novel_suite.core.paths import novels_dir, suite_root, video_root, writer_root

    root = suite_root()
    roots = [
        root,
        novels_dir(),
        video_root(),
        video_root() / "tmp",
        video_root() / "demos",
        writer_root(),
        writer_root() / "examples",
    ]
    intel = root / "intel"
    if intel.is_dir():
        roots.append(intel)
    deduped: list[Path] = []
    seen: set[str] = set()
    for r in roots:
        p = r.resolve()
        s = str(p)
        if s not in seen:
            seen.add(s)
            deduped.append(p)
    return deduped


def _path_within_roots(path: Path, roots: list[Path]) -> bool:
    resolved = path.resolve()
    for base in roots:
        try:
            resolved.relative_to(base)
            return True
        except ValueError:
            continue
    return False


def resolve_mcp_path(path_str: str, *, label: str = "path") -> Path:
    """Resolve MCP tool paths to suite subtree (files or write targets)."""
    if not path_str or not str(path_str).strip():
        raise ValueError(f"MCP {label}: empty path")
    raw = Path(path_str).expanduser()
    if raw.is_file() or raw.is_dir():
        resolved = raw.resolve()
    else:
        parent = raw.parent.expanduser()
        if not parent.exists():
            raise ValueError(f"MCP {label}: parent directory does not exist: {parent}")
        resolved = (parent.resolve() / raw.name)
    if not _path_within_roots(resolved, mcp_allowed_roots()):
        raise ValueError(
            f"MCP {label} out of bounds: {resolved} (must be under Novel Suite root, "
            "novels/, cursor-novel-video/, or writer examples)"
        )
    return resolved


def download_https_bytes(
    url: str,
    *,
    max_bytes: int = DOWNLOAD_MAX_BYTES,
    timeout_sec: float = DOWNLOAD_TIMEOUT_SEC,
    host_suffixes: tuple[str, ...] = _OPENAI_IMAGE_HOST_SUFFIXES,
) -> bytes:
    """Stream-download HTTPS URL with host allowlist and size cap."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("Only https URLs with a hostname are allowed")
    host = parsed.hostname.lower()
    if not any(host == s or host.endswith(f".{s}") for s in host_suffixes):
        raise ValueError(f"Download host not allowlisted: {host}")

    try:
        import httpx
    except ImportError as exc:
        raise RuntimeError("httpx required for URL download") from exc

    total = 0
    chunks: list[bytes] = []
    with httpx.Client(
        timeout=timeout_sec,
        follow_redirects=True,
        max_redirects=3,
    ) as client:
        with client.stream("GET", url) as resp:
            resp.raise_for_status()
            final = resp.url
            if final.scheme != "https" or not final.host:
                raise ValueError("Redirect left https")
            fh = final.host.lower()
            if not any(fh == s or fh.endswith(f".{s}") for s in host_suffixes):
                raise ValueError(f"Redirect host not allowlisted: {fh}")
            cl = resp.headers.get("content-length")
            if cl is not None:
                try:
                    if int(cl) > max_bytes:
                        raise ValueError(f"Content-Length exceeds {max_bytes} bytes")
                except ValueError as exc:
                    if "exceeds" in str(exc):
                        raise
            for chunk in resp.iter_bytes():
                total += len(chunk)
                if total > max_bytes:
                    raise ValueError(f"Download exceeds {max_bytes} bytes")
                chunks.append(chunk)
    return b"".join(chunks)
