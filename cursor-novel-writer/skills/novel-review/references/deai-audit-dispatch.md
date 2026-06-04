# De-AI 审计路由（L0 — Phase 7）

用户命令 → `modes` → 语料 → `novel audit deai`

| 用户关键词 | modes | 语料 |
| --- | --- | --- |
| 高频词、AI词、词表、lexicon | `lexicon` | [deai-corpus/lexicon.txt](./deai-corpus/lexicon.txt) |
| 修辞、句式、不是而是 | `rhetoric` | [rhetoric-patterns.md](./deai-corpus/rhetoric-patterns.md) |
| 叙事、说明体、段末升华 | `narrative` | [narrative-patterns.md](./deai-corpus/narrative-patterns.md) |
| 全量去AI、deai audit | `all` | 三者 |

## NEC 子任务

1. **P7-S0** 解析 modes（本表）
2. **P7-S1** `python engine/novel_cli.py audit deai --project . --chapter chapters/NN_*.md --json`
3. **P7-S2** Agent 读 `reviews/chNN-deai-scan.json` + [deai-checklist.md](./deai-checklist.md) + Sable
4. **P7-S3** 写入 `reviews/chNN-review.md` 的 `## De-AI` 与 `## De-AI Scan`
