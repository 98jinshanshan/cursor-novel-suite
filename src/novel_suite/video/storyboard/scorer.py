"""Scene importance scoring and duration allocation (C4-A02, C4-B04, C4-B05)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from novel_suite.video.storyboard.slicer import SceneSlice

#爽点 / 冲突 / 信息密度关键词（中文短视频叙事）
_PAYOFF_KEYWORDS = ("觉醒", "突破", "逆袭", "打脸", "获得", "震惊", "爆发", "反转", "真相")
_CONFLICT_KEYWORDS = ("对手", "危机", "对峙", "战斗", "威胁", "追", "杀", "怒", "险", "雨夜")
_INFO_KEYWORDS = ("新", "首次", "原来", "发现", "秘密", "记得", "十年前", "信封", "字")
_PROTAGONIST_HINTS = ("林墨", "林骁", "陈薇", "主角", "他", "她")

_SHOT_SIZES = ("wide", "medium", "close_up", "over_shoulder", "extreme_close")
_ANGLES = ("eye_level", "low", "high")
_MOVEMENTS = ("static", "pan", "zoom_in", "tracking")
_EMOTIONS = ("平静", "震惊", "愤怒", "悲伤", "紧张", "悬疑", "温馨", "热血", "恐惧")
_BGM_MOODS = ("紧张", "温馨", "热血", "悲伤", "悬疑")

_HOOK_MIN_SEC = 2.0
_HOOK_MAX_SEC = 5.0
_MIN_SCENE_SEC = 3.0
_MAX_SCENE_SEC = 15.0


@dataclass
class ScoredScene:
    scene_id: str
    narration: str
    importance_score: float
    duration_target: float
    shot_size: str
    angle: str
    movement: str
    emotion: str
    bgm_mood: str
    visual_job: str


def _keyword_density(text: str, keywords: tuple[str, ...]) -> float:
    if not text:
        return 0.0
    hits = sum(text.count(k) for k in keywords)
    return min(1.0, hits / max(1, len(text) / 80))


def _protagonist_weight(text: str) -> float:
    if any(name in text for name in _PROTAGONIST_HINTS):
        return 1.0
    if re.search(r"[「『].+[」』]", text):
        return 0.7
    return 0.35


def score_scene(slice_: SceneSlice) -> float:
    """Importance = payoff×0.4 + conflict×0.3 + role×0.2 + info×0.1."""
    text = slice_.text
    payoff = _keyword_density(text, _PAYOFF_KEYWORDS)
    conflict = _keyword_density(text, _CONFLICT_KEYWORDS)
    role = _protagonist_weight(text)
    info = _keyword_density(text, _INFO_KEYWORDS)
    return payoff * 0.4 + conflict * 0.3 + role * 0.2 + info * 0.1


def _pick_emotion(text: str, score: float) -> str:
    if "震惊" in text or "？" in text or "!" in text:
        return "震惊"
    if score >= 0.55:
        return "紧张"
    if any(k in text for k in ("雨", "雾", "夜", "暗")):
        return "悬疑"
    if any(k in text for k in ("笑", "暖", "光")):
        return "温馨"
    return "平静"


def _visual_job(score: float, index: int) -> str:
    if index == 0 or score >= 0.6:
        return "action"
    if score >= 0.4:
        return "consequence"
    if score >= 0.25:
        return "mechanism"
    return "transition"


def score_scenes(
    slices: list[SceneSlice],
    *,
    target_duration_sec: float = 60.0,
    hook_reserve_sec: float = 3.0,
) -> list[ScoredScene]:
    """Score slices and allocate per-scene duration within target total."""
    if not slices:
        return []

    raw_scores = [max(0.05, score_scene(s)) for s in slices]
    total_score = sum(raw_scores) or 1.0
    budget = max(target_duration_sec - hook_reserve_sec, len(slices) * _MIN_SCENE_SEC)

    scored: list[ScoredScene] = []
    for i, (sl, raw) in enumerate(zip(slices, raw_scores, strict=True)):
        share = raw / total_score
        duration = max(_MIN_SCENE_SEC, min(_MAX_SCENE_SEC, round(budget * share, 1)))
        emotion = _pick_emotion(sl.text, raw)
        scored.append(
            ScoredScene(
                scene_id=f"s{i + 1:02d}",
                narration=sl.narration,
                importance_score=round(raw, 4),
                duration_target=duration,
                shot_size=_SHOT_SIZES[i % len(_SHOT_SIZES)],
                angle=_ANGLES[i % len(_ANGLES)],
                movement=_MOVEMENTS[i % len(_MOVEMENTS)],
                emotion=emotion,
                bgm_mood=_BGM_MOODS[i % len(_BGM_MOODS)],
                visual_job=_visual_job(raw, i),
            )
        )
    return scored


def select_hook_shot(scored: list[ScoredScene]) -> dict[str, object]:
    """Pick highest-importance scene for opening hook (C4-B04)."""
    if not scored:
        return {"description": "", "duration": _HOOK_MIN_SEC, "scene_id": "s01"}

    best = max(scored, key=lambda s: s.importance_score)
    hook_dur = max(
        _HOOK_MIN_SEC,
        min(_HOOK_MAX_SEC, round(best.duration_target * 0.45, 1)),
    )
    desc = best.narration[:120] if best.narration else best.scene_id
    return {
        "description": desc,
        "duration": hook_dur,
        "scene_id": best.scene_id,
    }


def build_emotion_arc(scored: list[ScoredScene]) -> list[str]:
    """Summarize emotional rhythm across scenes (C4-B05)."""
    if not scored:
        return ["平静"]
    arc = [s.emotion for s in scored]
    # De-duplicate consecutive duplicates for readability
    compact: list[str] = []
    for em in arc:
        if not compact or compact[-1] != em:
            compact.append(em)
    return compact


def scored_to_storyboard_scenes(scored: list[ScoredScene]) -> list[dict[str, object]]:
    """Convert scored scenes to storyboard.json scene dicts."""
    return [
        {
            "id": s.scene_id,
            "narration": s.narration,
            "visual_job": s.visual_job,
            "duration_target": s.duration_target,
            "shot_size": s.shot_size,
            "angle": s.angle,
            "movement": s.movement,
            "emotion": s.emotion,
            "bgm_mood": s.bgm_mood,
            "importance_score": s.importance_score,
        }
        for s in scored
    ]
