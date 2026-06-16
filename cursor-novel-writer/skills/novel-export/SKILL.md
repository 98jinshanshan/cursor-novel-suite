---
name: novel-export
description: |
  Export chapters to EPUB ebook. Use for 导出epub、制作电子书、export epub, 把章节转成电子书.
license: MIT
compatibility: Requires Python 3.10+, ebooklib, and full repo clone (scripts/ wrapper → engine/).
metadata:
  author: cursor-novel-writer
  version: "1.0.0"
---

# Novel Export

## Node Execution Contract (NEC)

**执行前必读：** [references/node-dispatch.md](./references/node-dispatch.md)。  
导出后 `novel node sync --phase 9` → `canon/nodes/phase-9.completion.json`。

From novel-skill EPUB pipeline, generalized for Chinese typography.

## CLI

From repo root or skill context:

```bash
python skills/novel-export/scripts/create_epub.py --project . --output dist/书名.epub
```

Engine implementation: `engine/scripts/create_epub.py`

Or via novel CLI:

```bash
python engine/novel_cli.py export --format epub
```

## Steps (Agent)

1. Verify all chapters in `chapters/` match `chapters/_index.md`
2. Run Quill audit: [references/quill-export-audit.md](./references/quill-export-audit.md)
3. Read title/author from `story.md` frontmatter
4. Run create_epub.py
5. Report output path and chapter count

## EPUB Features

- Cover page (title, subtitle, author)
- Table of contents in chapter order
- Chinese-friendly CSS (indent, line-height)
- Optional intro from story.md premise

## Optional Exports

- **Markdown bundle**: copy chapters to `dist/manuscript.md`
- **Marketing** (Novel Master): title, blurb — user request only

## Sprint 5 新增

- 导出章节可直接用于番茄/起点/晋江发布准备（`dist/` 目录）
- `novel-suite novel publish upload --platform fanqie|qidian|jinjiang --project <path> --json`
- 番茄需 `novel-suite auth login --platform fanqie`（`FANQIE_API_KEY`）
