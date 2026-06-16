"""Storyboard engine — chapter slicing, scoring, schema validation (Sprint 2.1)."""

from novel_suite.video.storyboard.schema import (
    load_storyboard_schema,
    repair_storyboard,
    validate_storyboard,
)
from novel_suite.video.storyboard.generator import (
    StoryboardOptions,
    generate_storyboard,
    generate_storyboard_llm,
    generate_storyboard_rule,
    load_character_context,
)
from novel_suite.video.storyboard.scorer import score_scenes, select_hook_shot
from novel_suite.video.storyboard.slicer import SceneSlice, slice_chapter

__all__ = [
    "SceneSlice",
    "StoryboardOptions",
    "generate_storyboard",
    "generate_storyboard_llm",
    "generate_storyboard_rule",
    "load_character_context",
    "load_storyboard_schema",
    "repair_storyboard",
    "score_scenes",
    "select_hook_shot",
    "slice_chapter",
    "validate_storyboard",
]
