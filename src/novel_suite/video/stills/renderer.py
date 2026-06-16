"""Detect and select still rendering backend."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from novel_suite.core.paths import video_root
from novel_suite.video._legacy import load_video_script

_PROBE_TIMEOUT = 15.0


@dataclass
class StillBackend:
    """Detected still rendering capability."""

    name: str = "title_card"
    available: bool = True
    script: Path | None = None
    detail: str = ""

    def probe(self) -> StillBackend:
        """Detect backend priority: wan > sd > title_card."""
        adapters = video_root() / "adapters"
        scripts = video_root() / "engine" / "scripts"
        wan_script = adapters / "comfyui_wan_t2i.py"
        sd_script = adapters / "comfyui_render.py"
        title_script = scripts / "make_title_card.py"

        if wan_script.is_file():
            backend = self._probe_wan(wan_script)
            if backend is not None:
                return backend

        if sd_script.is_file():
            backend = self._probe_sd(sd_script)
            if backend is not None:
                return backend

        self.name = "title_card"
        self.available = True
        self.script = title_script if title_script.is_file() else None
        self.detail = "comfyui unavailable; using title_card fallback"
        return self

    def _run_probe(self, cmd: list[str]) -> str | None:
        try:
            run_command = load_video_script("subprocess_safe").run_command
            proc = run_command(
                cmd,
                capture_output=True,
                text=True,
                timeout=_PROBE_TIMEOUT,
                check=False,
            )
            if proc.returncode != 0:
                return None
            return proc.stdout or ""
        except (OSError, TimeoutError, ValueError):
            return None

    def _probe_wan(self, script: Path) -> StillBackend | None:
        out = self._run_probe([sys.executable, str(script), "--probe"])
        if out is None:
            return None
        try:
            data = json.loads(out)
        except json.JSONDecodeError:
            return None
        if not data.get("can_t2v_still"):
            return None
        return StillBackend(
            name="wan",
            available=True,
            script=script,
            detail="wan t2v still",
        )

    def _probe_sd(self, script: Path) -> StillBackend | None:
        out = self._run_probe([sys.executable, str(script), "--check"])
        if out is None:
            return None
        return StillBackend(
            name="sd",
            available=True,
            script=script,
            detail="comfyui sd render",
        )


@lru_cache(maxsize=1)
def get_backend() -> StillBackend:
    return StillBackend().probe()
