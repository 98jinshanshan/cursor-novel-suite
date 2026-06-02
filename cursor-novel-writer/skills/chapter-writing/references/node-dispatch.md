# Phase 5 节点分派（chapter-writing）

## Pre-write（必做）

| ID | 执行体 | 参考 |
| --- | --- | --- |
| P5-S0 | `cli` | `novel active` |
| P5-S1 | `agent` | `voice-brief.md`, `foreshadowing.md`, 上一章 |
| P5-S2 | `cli` | `graphify_bridge.py query`（可选） |

## Write

| ID | 执行体 | 产出 |
| --- | --- | --- |
| P5-S3 | `agent` | `chapters/NN_标题.md` |
| P5-S4 | `agent` | `canon/snapshots/chNN-after.md` |
| P5-S5 | `cli` | 更新 `canon/progress.json` |

## Post

| ID | 执行体 | 产出 |
| --- | --- | --- |
| P5-S6 | `cli` | `pipeline gate --phase 6` |
| P5-S7 | `cli` | `canon/nodes/phase-5.completion.json` |

## Chat Summary

章号、字数、钩子一句；正文仅摘要，全文在 chapters/。
