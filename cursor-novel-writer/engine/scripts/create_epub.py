#!/usr/bin/env python3
"""Export novel chapters to EPUB."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_story_meta(story_path: Path) -> dict[str, str]:
    text = story_path.read_text(encoding="utf-8")
    meta: dict[str, str] = {}
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"')
    return meta


def chapter_sort_key(path: Path) -> tuple:
    m = re.match(r"^(\d+)", path.stem)
    return (int(m.group(1)) if m else 9999, path.name)


def collect_chapters(project: Path) -> list[Path]:
    ch_dir = project / "chapters"
    if not ch_dir.is_dir():
        return []
    files = [p for p in ch_dir.glob("*.md") if not p.name.startswith("_")]
    return sorted(files, key=chapter_sort_key)


def markdown_to_html(md: str) -> str:
    html_lines = []
    for line in md.splitlines():
        if line.startswith("# "):
            html_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("---"):
            html_lines.append("<hr/>")
        elif line.strip() == "":
            html_lines.append("<p></p>")
        else:
            html_lines.append(f"<p>{line}</p>")
    return "\n".join(html_lines)


def build_epub(chapters: list[Path], title: str, author: str, output: Path) -> None:
    try:
        from ebooklib import epub
    except ImportError:
        print("ERROR: pip install ebooklib", file=sys.stderr)
        sys.exit(1)

    book = epub.EpubBook()
    book.set_identifier(f"novel-{datetime.now(timezone.utc).isoformat()}")
    book.set_title(title)
    book.set_language("zh")
    book.add_author(author or "Unknown")

    css = epub.EpubItem(
        uid="style",
        file_name="style/style.css",
        media_type="text/css",
        content="""
body { font-family: "Noto Serif SC", serif; line-height: 1.8; }
p { text-indent: 2em; margin: 0.5em 0; }
h1 { text-align: center; margin-top: 2em; }
h2 { margin-top: 1.5em; }
""".strip().encode("utf-8"),
    )
    book.add_item(css)

    spine: list[Any] = ["nav"]
    toc: list[Any] = []

    for i, ch_path in enumerate(chapters):
        raw = ch_path.read_text(encoding="utf-8")
        title_line = raw.splitlines()[0].lstrip("# ").strip() if raw else ch_path.stem
        html = markdown_to_html(raw)
        c = epub.EpubHtml(
            title=title_line,
            file_name=f"chap_{i+1:02d}.xhtml",
            lang="zh",
        )
        c.content = f'<html><head><link rel="stylesheet" href="style/style.css"/></head><body>{html}</body></html>'
        c.add_item(css)
        book.add_item(c)
        spine.append(c)
        toc.append(c)

    book.toc = toc
    book.add_item(epub.EpubNav())

    cover = epub.EpubHtml(title=title, file_name="cover.xhtml", lang="zh")
    cover.content = (
        f"<html><head></head><body><h1>{title}</h1><p>{author}</p></body></html>"
    )
    book.add_item(cover)
    spine = ["nav", cover, *spine[1:]]
    book.spine = spine
    epub.write_epub(str(output), book, {})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=Path, default=Path("."))
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()
    project = args.project.resolve()
    story = project / "story.md"
    meta = parse_story_meta(story) if story.exists() else {}
    title = (meta.get("title") or project.name).strip() or project.name
    author = (meta.get("author") or "作者").strip() or "作者"
    chapters = collect_chapters(project)
    if not chapters:
        print("ERROR: no chapters in chapters/", file=sys.stderr)
        return 1
    out = args.output or (project / "dist" / f"{title}.epub")
    out.parent.mkdir(parents=True, exist_ok=True)
    build_epub(chapters, title, author, out)
    print(f"OK: {out} ({len(chapters)} chapters)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
