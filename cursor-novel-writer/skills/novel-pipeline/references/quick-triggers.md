# Quick Trigger 一览（NS-11）

用户自然语言 → 应调用的 Skill / CLI。Agent 优先匹配本表，再 delegate。

| 用户说法（示例） | Skill / 命令 | 备注 |
| --- | --- | --- |
| 扫榜、题材雷达、热门题材、选题 | `novel-market-scan` | Phase 0 → `intel/radar/` |
| 新建小说、开书、立项 | `story-init` → `novel init` | 需 `--concept` 或 concept-brief |
| 写下一章、续写、继续写 | `chapter-writing` | 先 `novel active` |
| 审稿、一致性、查伏笔 | `novel-review` | `reviews/chNN-review.md` |
| 去 AI 味、润色前诊断 | `novel-review` Phase 7 | deai-checklist |
| 导出 epub、做电子书 | `novel-export` | `novel export --format epub` |
| 全流程、一键 pipeline | `novel-pipeline` | `novel pipeline status` |
| 换书、切小说 | `novel use <slug>` | 读 `novels/.active` |
| 创建人物、人物关系 | `character-management` | 双向关系见 references |
| 世界观、地点、规则 | `worldbuilding` | |
| 大纲、情节弧、伏笔表 | `plot-structure` | |
| 营销文案、简介 | `novel-marketing` | 用户明确要求时 |
| graphify 关系查询 | `novel graphify query` | 需 graphifyy + graph.json |

## CLI 速查

```bash
python engine/novel_cli.py intel paths
python engine/novel_cli.py intel scan --period week
python engine/novel_cli.py init --title "书名" --premise "..." --concept ../../intel/concepts/x.md
python engine/novel_cli.py pipeline gate --phase 1
python engine/novel_cli.py list
python engine/novel_cli.py active
python engine/novel_cli.py use <slug>
python engine/novel_cli.py pipeline status
python engine/novel_cli.py promote 01_标题.md
python engine/novel_cli.py bible summary
python engine/novel_cli.py graphify query --character "陈薇"
python engine/novel_cli.py export --format epub
```
