# Phase 6–8 节点分派（novel-review）

路由总表：[audit-dispatch-index.md](./audit-dispatch-index.md)

## Phase 6 验证

| ID | 执行体 | 参考 | 产出 |
| --- | --- | --- | --- |
| P6-S0 | `cli` | `graphify_bridge review` | graphify-out |
| P6-S1 | `agent` | [forge-workflow.md](./forge-workflow.md) 1–3 | `reviews/chNN-review.md` |
| P6-S4 | `cli` | `novel audit blocker` · `novel audit format` | `reviews/chNN-*-scan.json` |
| P6-S2 | `agent` | personas Ghostlight/Lumen | Blockers 节 `(none)` |
| P6-S3 | `cli` | `pipeline gate --phase 7` | 无 open blocker |

## Phase 7 去 AI

| ID | 执行体 | 参考 | 产出 |
| --- | --- | --- | --- |
| P7-S0 | `cli` | [deai-audit-dispatch.md](./deai-audit-dispatch.md) | 选定 modes |
| P7-S1 | `cli` | `novel audit deai --modes lexicon,rhetoric,narrative,all` | `reviews/chNN-deai-scan.json` |
| P7-S2 | `agent` | [deai-checklist.md](./deai-checklist.md) + [sable.md](./personas/sable.md) | 行级建议 |
| P7-S3 | `agent` | review `## De-AI Scan` + Platform 节 | `reviews/chNN-review.md` |

## Phase 8 再验证

| ID | 执行体 | 参考 | 产出 |
| --- | --- | --- | --- |
| P8-S0 | `cli` | `novel audit revalidate` | diff vs 上轮 scan |
| P8-S1 | `agent` | [review-repair-spec.md](../../../templates/review-repair-spec.md) | 修订稿 |
| P8-S2 | `agent` | 最多 2 轮 re-review | `## Re-validate` |
| P8-S3 | `cli` | `novel promote` 若用 `.drafts` | 正文晋升 |

## Chat Summary

Blocker 列表、De-AI scan 路径、`status`；报告在 `reviews/`。
