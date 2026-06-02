# 工作流导航（Novel Suite）

**Agent 主入口：** [AGENTS.md](../../AGENTS.md)  
**节点执行契约：** [NODE-EXECUTION-CONTRACT.md](../standards/NODE-EXECUTION-CONTRACT.md)  
**加厚矩阵：** [NEC-10-enrichment-matrix.md](../plans/NEC-10-enrichment-matrix.md)

## 执行链（每次请求）

```text
用户自然语言
  → novel-pipeline（宏观 Phase）
  → 原子 Skill NEC + node-dispatch.md
  → CLI / Agent 分派执行
  → 落盘产物 + *.completion.json
  → 对话框摘要
  → pipeline gate / node validate
```

## Phase 索引

| Phase | Skill | 分派文档 |
| --- | --- | --- |
| 0 | novel-market-scan | [node-dispatch.md](../../cursor-novel-writer/skills/novel-market-scan/references/node-dispatch.md) |
| 1 | story-init | [node-dispatch.md](../../cursor-novel-writer/skills/story-init/references/node-dispatch.md) |
| 2a | worldbuilding | [node-dispatch.md](../../cursor-novel-writer/skills/worldbuilding/references/node-dispatch.md) |
| 2b | character-management | [node-dispatch.md](../../cursor-novel-writer/skills/character-management/references/node-dispatch.md) |
| 3 | plot-structure | [node-dispatch.md](../../cursor-novel-writer/skills/plot-structure/references/node-dispatch.md) |
| 4 | voice-brief 模板 | [phase-4-node-dispatch.md](../../cursor-novel-writer/templates/references/phase-4-node-dispatch.md) · `templates/voice-brief.md` |
| 5 | chapter-writing | [node-dispatch.md](../../cursor-novel-writer/skills/chapter-writing/references/node-dispatch.md) |
| 6–8 | novel-review | [node-dispatch.md](../../cursor-novel-writer/skills/novel-review/references/node-dispatch.md) |
| 9 | novel-export | [node-dispatch.md](../../cursor-novel-writer/skills/novel-export/references/node-dispatch.md) |

## 视频

| 节点 | Skill | 分派文档 |
| --- | --- | --- |
| V0 | video-chapter-summary | [node-dispatch.md](../../cursor-novel-video/skills/video-chapter-summary/references/node-dispatch.md) |
| V1 | video-scene-drama | [node-dispatch.md](../../cursor-novel-video/skills/video-scene-drama/references/node-dispatch.md) |
| V2 | video-export | [node-dispatch.md](../../cursor-novel-video/skills/video-export/references/node-dispatch.md) |

## 多 IDE

Skills 源目录：`cursor-novel-writer/skills/`、`cursor-novel-video/skills/`  
安装：`platforms/install-skills.ps1` → Cursor / Qoder / TRAE-CN 一致。
