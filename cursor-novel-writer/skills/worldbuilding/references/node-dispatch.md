# Phase 2a 节点分派（worldbuilding）

## Dispatch Table

| ID | 执行体 | 产出 |
| --- | --- | --- |
| P2a-S0 | `cli` `novel active` | active slug |
| P2a-S1 | `agent` 地点/系统模板 | `worldbuilding/locations/*.md`, `systems/*.md` |
| P2a-S2 | `agent` | `worldbuilding/_index.md` 更新 |
| P2a-S3 | `cli` `pipeline gate --phase 3` | gate OK |
| P2a-S4 | `cli` `node validate --phase 2` | `canon/nodes/phase-2.completion.json`（与人物共享 phase 2） |

## Chat Summary

≥1 location 或 system 路径列表；禁止只描述不写文件。
