# Phase 2b 节点分派（character-management）

## Dispatch Table

| ID | 执行体 | 产出 |
| --- | --- | --- |
| P2b-S0 | `cli` `novel active` | active slug |
| P2b-S1 | `agent` 人物卡 | `characters/*.md`（≥2） |
| P2b-S2 | `agent` [bidirectional-relations.md](./bidirectional-relations.md) | 关系双向一致 |
| P2b-S3 | `cli` `novel relations check` | 无 ERROR |
| P2b-S4 | `cli` `pipeline gate --phase 3` | gate OK |

## Gate

Phase 3 需 ≥2 characters + ≥1 location/system
