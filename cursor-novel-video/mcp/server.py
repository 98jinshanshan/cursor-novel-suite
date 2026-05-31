"""
Optional MCP server for novel-video: render + subtitle tools.
Run: python mcp/server.py (requires mcp package: pip install mcp)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "engine" / "scripts"
CLI = ROOT / "engine" / "video_cli.py"


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
        cmd = [sys.executable, str(CLI), "summary", "--chapter", chapter_path, "--aspect", aspect]
        if subtitles:
            cmd.append("--subtitles")
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.stdout + r.stderr

    @mcp.tool()
    def render_drama(chapter_path: str, aspect: str = "9:16", subtitles: bool = False) -> str:
        """Render per-scene drama video (knowledge-video style segments)."""
        cmd = [sys.executable, str(CLI), "drama", "--chapter", chapter_path, "--aspect", aspect]
        if subtitles:
            cmd.append("--subtitles")
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.stdout + r.stderr

    @mcp.tool()
    def qc_video(path: str) -> str:
        """Run ffprobe QC on video file."""
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "qc_video.py"), path, "--require-audio"],
            capture_output=True,
            text=True,
        )
        return r.stdout + r.stderr

    @mcp.tool()
    def generate_subtitles(script_path: str, audio_path: str, output_srt: str, whisper: bool = False) -> str:
        """Beat-lock: script + audio → SRT (optional Whisper alignment)."""
        cmd = [
            sys.executable,
            str(SCRIPTS / "beat_lock.py"),
            "--script",
            script_path,
            "--audio",
            audio_path,
            "--output",
            output_srt,
        ]
        if whisper:
            cmd.append("--whisper")
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.stdout + r.stderr

    @mcp.tool()
    def burn_subtitles(video_path: str, srt_path: str, output_path: str) -> str:
        """Burn SRT subtitles into MP4."""
        r = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "burn_subtitles.py"),
                "--video",
                video_path,
                "--srt",
                srt_path,
                "--output",
                output_path,
            ],
            capture_output=True,
            text=True,
        )
        return r.stdout + r.stderr

    mcp.run()


if __name__ == "__main__":
    try_mcp()
