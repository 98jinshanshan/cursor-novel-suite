# 审计与规范参照索引（NEC-11）

| Phase | L0 路由 | L1 语料 | L2 脚本 | 对话入口 |
| --- | --- | --- | --- | --- |
| 0 | [platform-scan-guide](../../cursor-novel-writer/skills/novel-market-scan/references/platform-scan-guide.md) | [platform-length-corpus.md](../../cursor-novel-writer/skills/novel-market-scan/references/platform-length-corpus.md) | `intel_rubric_score.py` | `novel audit intel` |
| 1 | [story-init node-dispatch](../../cursor-novel-writer/skills/story-init/references/node-dispatch.md) | [story-template.md](../../cursor-novel-writer/skills/story-init/references/story-template.md) | `story_init_audit.py` | `novel audit story` |
| 2 | [character](../../cursor-novel-writer/skills/character-management/references/node-dispatch.md) / [world](../../cursor-novel-writer/skills/worldbuilding/references/node-dispatch.md) | [bidirectional-relations.md](../../cursor-novel-writer/skills/character-management/references/bidirectional-relations.md) | `canon_lint.py` | `novel audit canon` |
| 3 | [plot node-dispatch](../../cursor-novel-writer/skills/plot-structure/references/node-dispatch.md) | [plot-frameworks.md](../../cursor-novel-writer/skills/plot-structure/references/plot-frameworks.md) | `plot_scale_audit.py` | `novel audit plot` |
| 4 | [phase-4-node-dispatch](../../cursor-novel-writer/templates/references/phase-4-node-dispatch.md) | [voice-brief.md](../../cursor-novel-writer/templates/voice-brief.md) | `voice_brief_lint.py` | `novel audit voice` |
| 5 | [chapter-writing](../../cursor-novel-writer/skills/chapter-writing/references/chapter-format.md) | [chinese-prose-layout.md](../../cursor-novel-writer/skills/chapter-writing/references/chinese-prose-layout.md) | `chapter_format_lint.py` | `novel audit format` |
| 6–8 | [audit-dispatch-index](../../cursor-novel-writer/skills/novel-review/references/audit-dispatch-index.md) | [deai-corpus](../../cursor-novel-writer/skills/novel-review/references/deai-corpus/README.md) | `review_blocker_scan.py` / `deai_audit.py` / `revalidate_diff.py` | 见 novel-review |
| 9 | [novel-export node-dispatch](../../cursor-novel-writer/skills/novel-export/references/node-dispatch.md) | [quill-export-audit.md](../../cursor-novel-writer/skills/novel-export/references/quill-export-audit.md) | `export_audit.py` | `novel audit export` |
| V0 | [video V0 dispatch](../../cursor-novel-video/skills/video-chapter-summary/references/node-dispatch.md) | [PIPELINE.md](../../cursor-novel-video/skills/video-chapter-summary/references/PIPELINE.md) | `video_script_lint.py` | `novel audit video-script` |

总路由：[audit-dispatch-index.md](../../cursor-novel-writer/skills/novel-review/references/audit-dispatch-index.md)  
全景图：[NEC-NODE-MAP.md](../workflow/NEC-NODE-MAP.md)
