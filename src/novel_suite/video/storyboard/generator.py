"""Storyboard generation — rule-based default + optional Ollama LLM (Sprint 2.1b)."""

from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from novel_suite.core import errors as E
from novel_suite.core.env_config import get_ollama_host
from novel_suite.core.prompt_template import safe_json_prompt
from novel_suite.core.sanitizer import filter_llm_output, sanitize_prompt_input
from novel_suite.memory.recall import recall_for_video
from novel_suite.memory.store import MemoryStore
from novel_suite.video.storyboard.schema import (
    load_storyboard_schema,
    repair_storyboard,
    validate_storyboard,
)
from novel_suite.video.storyboard.scorer import (
    ScoredScene,
    build_emotion_arc,
    score_scenes,
    scored_to_storyboard_scenes,
    select_hook_shot,
)
from novel_suite.video.storyboard.slicer import SceneSlice, slice_chapter

_log = logging.getLogger(__name__)

_DEFAULT_OLLAMA_MODEL = "llama3.2"
_OLLAMA_TIMEOUT_SEC = 60

_SYSTEM_INSTRUCTION = """你是一位专业短视频分镜师。将小说章节转换为 60 秒竖屏短视频分镜 JSON。

核心规则：
1. 总时长约 60 秒，6–12 个镜头（scenes）
2. 前 3 秒必须有视觉冲击力强的 hook_shot
3. 每个 scene 含 narration、visual_job、duration_target
4. 爽点/高潮场景分配更多 duration_target
5. 角色形象必须与角色设定一致
6. 仅输出 JSON，不要其他文字"""


@dataclass
class StoryboardOptions:
    job_id: str = "storyboard-draft"
    source_chapter: str = "ch01"
    chapter_key: str = ""
    mode: str = "summary"
    aspect: str = "9:16"
    target_duration_sec: int = 60
    min_scenes: int = 6
    max_scenes: int = 12
    voice: str = "zh-CN-XiaoxiaoNeural"
    novel_meta: dict[str, Any] = field(default_factory=dict)


def load_character_context(
    project: Path | None,
    *,
    query: str = "角色",
) -> str:
    """Load character summaries from memory L4 and/or canon/characters/*.md."""
    if project is None:
        return ""

    parts: list[str] = []
    try:
        store = MemoryStore(project)
        hits = recall_for_video(store, query, tags=["character"], limit=5)
        for hit in hits:
            text = str(hit.get("text", "")).strip()
            if text:
                parts.append(text)
    except Exception as exc:  # noqa: BLE001 — optional memory path
        _log.debug("memory character recall skipped: %s", exc)

    chars_dir = project / "characters"
    if chars_dir.is_dir():
        for md in sorted(chars_dir.glob("*.md")):
            if md.name.startswith("_"):
                continue
            snippet = md.read_text(encoding="utf-8")[:500].strip()
            if snippet:
                parts.append(f"# {md.stem}\n{snippet}")
            if len(parts) >= 8:
                break

    combined = "\n\n".join(parts)
    return sanitize_prompt_input(combined)[:2000]


def assemble_storyboard(
    scored: list[ScoredScene],
    *,
    options: StoryboardOptions,
    character_profiles: str = "",
) -> dict[str, Any]:
    """Build storyboard dict from scored scenes."""
    payload: dict[str, Any] = {
        "job_id": options.job_id,
        "source_chapter": options.source_chapter or options.chapter_key or "ch01",
        "mode": options.mode,
        "aspect": options.aspect,
        "target_duration_sec": options.target_duration_sec,
        "voice": options.voice,
        "hook_shot": select_hook_shot(scored),
        "emotion_arc": build_emotion_arc(scored),
        "scenes": scored_to_storyboard_scenes(scored),
        "generator": "rule",
    }
    if options.novel_meta:
        payload["novel"] = options.novel_meta
    if character_profiles:
        payload["character_profiles_digest"] = character_profiles[:200]
    return repair_storyboard(payload, default_mode=options.mode)


def generate_storyboard_rule(
    chapter_text: str,
    *,
    options: StoryboardOptions | None = None,
    character_profiles: str = "",
    scored: list[ScoredScene] | None = None,
    slices: list[SceneSlice] | None = None,
) -> dict[str, Any]:
    """Rule-based storyboard (CI default, no Ollama)."""
    opts = options or StoryboardOptions()
    safe_text = sanitize_prompt_input(chapter_text)

    if scored is None:
        if slices is None:
            slices = slice_chapter(
                safe_text,
                min_scenes=opts.min_scenes,
                max_scenes=opts.max_scenes,
            )
        scored = score_scenes(
            slices,
            target_duration_sec=float(opts.target_duration_sec),
        )

    board = assemble_storyboard(scored, options=opts, character_profiles=character_profiles)
    errors = validate_storyboard(board)
    if errors:
        board = repair_storyboard(board, default_mode=opts.mode)
    return board


def ollama_available(*, host: str | None = None, timeout_sec: float = 2.0) -> bool:
    base = (host or get_ollama_host()).rstrip("/")
    try:
        req = urllib.request.Request(f"{base}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def _extract_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned)
    if fence:
        cleaned = fence.group(1).strip()
    data = json.loads(cleaned)
    if not isinstance(data, dict):
        raise ValueError("LLM output is not a JSON object")
    return data


def _call_ollama(
    prompt: str,
    *,
    host: str | None = None,
    model: str = _DEFAULT_OLLAMA_MODEL,
    timeout_sec: int = _OLLAMA_TIMEOUT_SEC,
) -> str:
    base = (host or get_ollama_host()).rstrip("/")
    body = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        },
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    response = str(payload.get("response", "")).strip()
    if not response:
        raise RuntimeError("empty Ollama response")
    return response


def generate_storyboard_llm(
    chapter_text: str,
    *,
    options: StoryboardOptions | None = None,
    project: Path | None = None,
    character_profiles: str = "",
    model: str = _DEFAULT_OLLAMA_MODEL,
    ollama_host: str | None = None,
    fallback_to_rule: bool = True,
) -> tuple[dict[str, Any], Literal["llm", "rule"]]:
    """
    LLM storyboard via Ollama + safe_json_prompt.
    Falls back to rule generator when Ollama unavailable or output invalid.
    """
    opts = options or StoryboardOptions()
    profiles = character_profiles or load_character_context(project)

    if not ollama_available(host=ollama_host):
        if fallback_to_rule:
            return generate_storyboard_rule(chapter_text, options=opts, character_profiles=profiles), "rule"
        raise RuntimeError(E.STORYBOARD_LLM_UNAVAILABLE)

    schema_json = json.dumps(load_storyboard_schema(), ensure_ascii=False, indent=2)
    user_block = f"章节内容：\n{sanitize_prompt_input(chapter_text)}\n\n角色设定：\n{profiles or '（无）'}"
    prompt = safe_json_prompt(_SYSTEM_INSTRUCTION, user_block, schema_json)

    try:
        raw = _call_ollama(prompt, host=ollama_host, model=model)
        filtered = filter_llm_output(raw)
        if not filtered.safe:
            raise ValueError(f"LLM output filtered: {filtered.violations}")
        parsed = _extract_json_object(raw)
        board = repair_storyboard({**parsed, "generator": "llm"}, default_mode=opts.mode)
        if opts.job_id and board.get("job_id") == "storyboard-draft":
            board["job_id"] = opts.job_id
        errors = validate_storyboard(board)
        if errors:
            raise ValueError(f"schema invalid: {errors[:3]}")
        return board, "llm"
    except Exception as exc:  # noqa: BLE001 — fallback path
        _log.info("storyboard LLM fallback to rule: %s", exc)
        if fallback_to_rule:
            return generate_storyboard_rule(chapter_text, options=opts, character_profiles=profiles), "rule"
        raise RuntimeError(E.STORYBOARD_FAILED) from exc


def generate_storyboard(
    chapter_text: str,
    *,
    use_llm: bool = False,
    options: StoryboardOptions | None = None,
    project: Path | None = None,
    character_profiles: str = "",
    **llm_kwargs: Any,
) -> tuple[dict[str, Any], Literal["llm", "rule"]]:
    """Unified entry — rule by default; optional LLM when use_llm=True."""
    opts = options or StoryboardOptions()
    profiles = character_profiles or load_character_context(project)
    if use_llm:
        return generate_storyboard_llm(
            chapter_text,
            options=opts,
            project=project,
            character_profiles=profiles,
            **llm_kwargs,
        )
    return generate_storyboard_rule(chapter_text, options=opts, character_profiles=profiles), "rule"
