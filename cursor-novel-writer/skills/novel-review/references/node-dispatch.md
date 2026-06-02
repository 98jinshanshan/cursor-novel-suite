# Phase 6–8 节点分派（novel-review）

## Phase 6 验证

| ID | 执行体 | 参考 | 产出 |
| --- | --- | --- | --- |
| P6-S0 | `cli` | `graphify_bridge review` | graphify-out |
| P6-S1 | `agent` | [forge-workflow.md](./forge-workflow.md) 1–3 | `reviews/chNN-review.md` |
| P6-S2 | `agent` | personas Ghostlight/Lumen | Blockers 节 |
| P6-S3 | `cli` | `pipeline gate --phase 7` | 无 open blocker |

## Phase 7 去 AI

| ID | 执行体 | 产出 |
| --- | --- | --- |
| P7-S1 | `agent` | [deai-checklist.md](./deai-checklist.md) |
| P7-S2 | `agent` | persona Sable |
| P7-S3 | `agent` | review `## De-AI` + Platform 节 |

## Phase 8 再验证

| ID | 执行体 | 产出 |
| --- | --- | --- |
| P8-S1 | `agent` | [review-repair-spec.md](../../../templates/review-repair-spec.md) |
| P8-S2 | `agent` | 最多 2 轮 re-review |
| P8-S3 | `cli` | `novel promote` 若用 .drafts |

## Chat Summary

Blocker 列表、De-AI 是否全绿；报告路径 reviews/。
