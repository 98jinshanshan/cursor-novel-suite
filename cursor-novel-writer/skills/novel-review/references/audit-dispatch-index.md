# 审计路由总表（NEC-11 L0）

用户「审计/检查/lint」→ `novel audit <mode>`

| 关键词 | mode | 分派 | 脚本 |
| --- | --- | --- | --- |
| 格式、缩进、一二三 | `format` | [chapter-format.md](../../chapter-writing/references/chapter-format.md) | `chapter_format_lint.py` |
| 去AI、高频词 | `deai` | [deai-audit-dispatch.md](./deai-audit-dispatch.md) | `deai_audit.py` |
| 文风契约 | `voice` | [voice-brief 模板](../../../templates/voice-brief.md) | `voice_brief_lint.py` |
| 大纲篇幅、分卷 | `plot` | [plot-frameworks.md](../../plot-structure/references/plot-frameworks.md) | `plot_scale_audit.py` |
| 立项 | `story` | [story-init](../story-init/SKILL.md) | `story_init_audit.py` |
| 设定人物 | `canon` | [character-management](../../character-management/SKILL.md) | `canon_lint.py` |
| 硬校验、blocker | `blocker` | [forge-workflow.md](./forge-workflow.md) | `review_blocker_scan.py` |
| 再验证 | `revalidate` | [review-repair-spec](../../../templates/review-repair-spec.md) | `revalidate_diff.py` |
| 导出 | `export` | [quill-export-audit.md](../../novel-export/references/quill-export-audit.md) | `export_audit.py` |
| 雷达结构 | `intel` | [platform-scan-guide](../../novel-market-scan/references/platform-scan-guide.md) | `intel_rubric_score.py` |
| 视频脚本 | `video-script` | [PIPELINE.md](../../../../cursor-novel-video/skills/video-chapter-summary/references/PIPELINE.md) | `video_script_lint.py` |

```bash
python engine/novel_cli.py audit format --project novels/<slug> --chapter chapters/01_*.md --json
python engine/novel_cli.py audit deai --project novels/<slug> --modes lexicon,rhetoric --json
```

索引：[AUDIT-REFERENCES-INDEX.md](../../../../docs/standards/AUDIT-REFERENCES-INDEX.md)
