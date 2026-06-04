"""NEC-11: shared helpers for audit/lint scripts."""

from __future__ import annotations

import re
from pathlib import Path

from scripts import suite_paths as sp

WRITER_ROOT = sp.writer_root()
SKILLS_REVIEW = WRITER_ROOT / "skills" / "novel-review" / "references"
DEAI_CORPUS = SKILLS_REVIEW / "deai-corpus"
MARKET_SCAN_REFS = WRITER_ROOT / "skills" / "novel-market-scan" / "references"

CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def count_cjk(text: str) -> int:
    return len(CJK_RE.findall(text))


def resolve_chapter(project: Path, chapter_arg: str | None) -> Path:
    project = project.resolve()
    if chapter_arg:
        ch = Path(chapter_arg)
        if not ch.is_absolute():
            ch = project / ch
        return ch.resolve()
    chapters = sorted(project.glob("chapters/*.md"))
    chapters = [p for p in chapters if not p.name.startswith("_")]
    if not chapters:
        raise FileNotFoundError(f"No chapters under {project / 'chapters'}")
    return chapters[-1].resolve()


def chapter_display_path(project: Path, chapter_path: Path) -> str:
    try:
        return str(chapter_path.resolve().relative_to(project.resolve())).replace("\\", "/")
    except ValueError:
        return chapter_path.name


def chapter_stem(chapter_path: Path) -> str:
    """e.g. ch03 from 03_暗格.md or reviews naming."""
    name = chapter_path.stem
    m = re.match(r"^(\d+)", name)
    if m:
        return f"ch{int(m.group(1)):02d}"
    return f"ch_{name[:20]}"


def default_scan_path(project: Path, chapter_path: Path, suffix: str) -> Path:
    return project / "reviews" / f"{chapter_stem(chapter_path)}-{suffix}-scan.json"


def load_lexicon_lines(path: Path) -> list[str]:
    if not path.is_file():
        return []
    terms: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        terms.append(s)
    return terms


def load_rhetoric_patterns(corpus_dir: Path) -> list[tuple[str, str, str]]:
    """Return (rule_id, regex, description) from rhetoric-patterns.md code blocks."""
    path = corpus_dir / "rhetoric-patterns.md"
    if not path.is_file():
        return _builtin_rhetoric_patterns()
    patterns: list[tuple[str, str, str]] = []
    text = path.read_text(encoding="utf-8")
    for block in re.finditer(r"```regex\n(.*?)```", text, re.DOTALL):
        body = block.group(1).strip()
        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("|", 2)
            if len(parts) >= 3:
                patterns.append((parts[0].strip(), parts[1].strip(), parts[2].strip()))
    return patterns or _builtin_rhetoric_patterns()


def load_narrative_patterns(corpus_dir: Path) -> list[tuple[str, str, str]]:
    path = corpus_dir / "narrative-patterns.md"
    if not path.is_file():
        return _builtin_narrative_patterns()
    patterns: list[tuple[str, str, str]] = []
    text = path.read_text(encoding="utf-8")
    for block in re.finditer(r"```regex\n(.*?)```", text, re.DOTALL):
        body = block.group(1).strip()
        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("|", 2)
            if len(parts) >= 3:
                patterns.append((parts[0].strip(), parts[1].strip(), parts[2].strip()))
    return patterns or _builtin_narrative_patterns()


def _builtin_rhetoric_patterns() -> list[tuple[str, str, str]]:
    return [
        (
            "rhetoric.not_a_but_b",
            r"不是[^，。！？\n]{1,40}，?而是",
            "「不是…而是…」句式",
        ),
        (
            "rhetoric.is_not_but",
            r"是[^，。！？\n]{1,30}，?不是[^，。！？\n]{1,30}，?而是",
            "「是…不是…而是…」句式",
        ),
        (
            "rhetoric.however_stack",
            r"(然而|但是|不过|可是)([^。！？\n]*)(然而|但是|不过|可是)",
            "同段转折词堆叠",
        ),
    ]


def _builtin_narrative_patterns() -> list[tuple[str, str, str]]:
    return [
        (
            "narrative.felt_wave",
            r"感到[^。！？\n]{0,12}(涌上心头|袭来|席卷)",
            "「感到…涌上心头」模板",
        ),
        (
            "narrative.as_you_know",
            r"正如你所知|众所周知|不难看出|值得注意的是",
            "说明体/综述体插入",
        ),
        (
            "narrative.eyes",
            r"(目光|眼神|视线)",
            "眼神/目光描写（检查密度）",
        ),
    ]


def parse_story_meta(story_path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not story_path.is_file():
        return out
    for line in story_path.read_text(encoding="utf-8").splitlines():
        if line.strip() == "---":
            break
        if ":" in line:
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip().strip('"')
    return out


def parse_voice_brief_fields(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    if not path.is_file():
        return fields
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*(\w+)\s*\|\s*([^|]+)\|", line)
        if m and m.group(1) not in ("项", "字段"):
            fields[m.group(1)] = m.group(2).strip()
    return fields
