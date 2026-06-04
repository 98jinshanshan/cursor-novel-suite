"""
Optional MCP server for novel-video: render + subtitle tools.
Run: python mcp/server.py (requires mcp package: pip install mcp)

Security: stdio/local use only — do not bind to a public network without auth.
Paths must resolve under the Novel Suite monorepo (see path_guard).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_MCP_DIR = Path(__file__).resolve().parent
if str(_MCP_DIR) not in sys.path:
    sys.path.insert(0, str(_MCP_DIR))
from path_guard import resolve_mcp_path  # noqa: E402

ROOT = _MCP_DIR.parent
SCRIPTS = ROOT / "engine" / "scripts"
CLI = ROOT / "engine" / "video_cli.py"


def _guard(path_str: str, *, label: str) -> str:
    return str(resolve_mcp_path(path_str, label=label))


def try_mcp():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        print("Install: pip install mcp", file=sys.stderr)
        sys.exit(1)
    mcp = FastMCP("novel-video")

    @mcp.tool()
    def render_summary(chapter_path: str, aspect: str = "9:16", subtitles: bool = False) -> str:
        """Render chapter summary video from markdown chapter file."""
        chapter = _guard(chapter_path, label="chapter_path")
        cmd = [sys.executable, str(CLI), "summary", "--chapter", chapter, "--aspect", aspect]
        if subtitles:
            cmd.append("--subtitles")
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.stdout + r.stderr

    @mcp.tool()
    def render_drama(chapter_path: str, aspect: str = "9:16", subtitles: bool = False) -> str:
        """Render per-scene drama video (knowledge-video style segments)."""
        chapter = _guard(chapter_path, label="chapter_path")
        cmd = [sys.executable, str(CLI), "drama", "--chapter", chapter, "--aspect", aspect]
        if subtitles:
            cmd.append("--subtitles")
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.stdout + r.stderr

    @mcp.tool()
    def qc_video(path: str) -> str:
        """Run ffprobe QC on video file."""
        video = _guard(path, label="path")
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "qc_video.py"), video, "--require-audio"],
            capture_output=True,
            text=True,
        )
        return r.stdout + r.stderr

    @mcp.tool()
    def generate_subtitles(script_path: str, audio_path: str, output_srt: str, whisper: bool = False) -> str:
        """Beat-lock: script + audio → SRT (optional Whisper alignment)."""
        script = _guard(script_path, label="script_path")
        audio = _guard(audio_path, label="audio_path")
        output = _guard(output_srt, label="output_srt")
        cmd = [
            sys.executable,
            str(SCRIPTS / "beat_lock.py"),
            "--script",
            script,
            "--audio",
            audio,
            "--output",
            output,
        ]
        if whisper:
            cmd.append("--whisper")
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.stdout + r.stderr

    @mcp.tool()
    def burn_subtitles(video_path: str, srt_path: str, output_path: str) -> str:
        """Burn SRT subtitles into MP4."""
        video = _guard(video_path, label="video_path")
        srt = _guard(srt_path, label="srt_path")
        output = _guard(output_path, label="output_path")
        r = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "burn_subtitles.py"),
                "--video",
                video,
                "--srt",
                srt,
                "--output",
                output,
            ],
            capture_output=True,
            text=True,
        )
        return r.stdout + r.stderr

    mcp.run()


if __name__ == "__main__":
    try_mcp()
