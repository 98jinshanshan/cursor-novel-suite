# Phase 9 节点分派（novel-export）

| ID | 执行体 | 命令 | 产出 |
| --- | --- | --- | --- |
| P9-S0 | `cli` | `pipeline gate --phase 9` | 预检通过 |
| P9-S1 | `agent` | [quill-export-audit.md](./quill-export-audit.md) | 审计勾选 |
| P9-S2 | `cli` | `skills/novel-export/scripts/create_epub.py` | `dist/*.epub` |
| P9-S3 | `cli` | `node validate --phase 9` | `phase-9.completion.json` |

## Chat Summary

EPUB 路径、章节数；可选 delegate `novel-marketing` 文案。
