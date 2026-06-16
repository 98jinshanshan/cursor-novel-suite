"""Still keyframe generation pipeline — Sprint 2.3a."""

from novel_suite.video.stills.generator import generate_stills
from novel_suite.video.stills.renderer import StillBackend, get_backend

__all__ = ["StillBackend", "generate_stills", "get_backend"]
