"""Character consistency check — lightweight field-level verification."""

from __future__ import annotations

from typing import Any


def check_character_consistency(
    character_profiles: dict[str, Any],
    storyboard_scenes: list[dict[str, Any]],
) -> dict[str, Any]:
    """Check that characters mentioned in storyboard have visual profile metadata."""
    if not character_profiles:
        return {
            "passed": False,
            "issues": [
                {
                    "character": "*",
                    "severity": "high",
                    "detail": "No character profiles found — run character pack first",
                }
            ],
            "mode": "field_level",
        }

    cvdp_names = set(character_profiles.keys())
    sb_mentions: set[str] = set()

    for scene in storyboard_scenes:
        narration = str(scene.get("narration", "") or "")
        for name in cvdp_names:
            if name in narration:
                sb_mentions.add(name)

    issues: list[dict[str, Any]] = []
    for name in sorted(sb_mentions):
        profile = character_profiles.get(name, {})
        if not profile.get("ref_prompt_positive"):
            issues.append(
                {
                    "character": name,
                    "severity": "medium",
                    "detail": (
                        f"'{name}' has no ref_prompt_positive — "
                        "still image may not match description"
                    ),
                }
            )
        if not profile.get("consistency_token"):
            issues.append(
                {
                    "character": name,
                    "severity": "low",
                    "detail": (
                        f"'{name}' has no consistency_token — "
                        "cross-shot consistency not enforced"
                    ),
                }
            )

    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "mode": "field_level",
        "characters_in_storyboard": sorted(sb_mentions),
        "characters_in_cvdp": len(cvdp_names),
    }
