# Phase 3 节点分派（plot-structure）

## Dispatch Table

| ID | 执行体 | 产出 |
| --- | --- | --- |
| P3-S0 | `agent` [plot-frameworks.md](./plot-frameworks.md) | 选定结构 |
| P3-S1 | `agent` | `plot/arcs/*.md`（≥1） |
| P3-S2 | `agent` | `plot/foreshadowing.md` 矩阵 |
| P3-S5 | `agent` | 模板 [plot-master-12.md](../../../templates/plot-master-12.md)、[plot-chapter-plan.md](../../../templates/plot-chapter-plan.md) |
| P3-S6 | `cli` | `novel audit plot --json` |
| P3-S3 | `cli` `pipeline gate --phase 4` | gate OK |
| P3-S4 | `cli` `node validate --phase 3` | `canon/nodes/phase-3.completion.json` |

## Chat Summary

弧名称、伏笔条数；矩阵须落盘。
