# cursor-novel-writer

中文通用小说创作工具包：**开放 Agent Skills 标准** + **独立 CLI** + **graphify 知识图谱一致性**。

Monorepo 审计与目录规范：[docs/INDEX.md](../docs/INDEX.md)

融合项目：

- [story-skills](https://github.com/danjdewhurst/story-skills)
- [novel-skill](https://github.com/mave99a/novel-skill)
- [graphify-novel](https://github.com/Anshler/graphify-novel)
- zencoder-novel-engine 编辑人格、postwriter 校验方法论

## 兼容平台

| 平台 | 安装 |
| --- | --- |
| Cursor | `npx skills add <repo> -a cursor -y` |
| Qoder | `-a qoder` → `.qoder/skills/` |
| TRAE CN / SOLO | `-a trae-cn` → `.trae/skills/` |
| Claude Code / Codex / Copilot | [agentskills.io](https://agentskills.io) 通用 |

一键多平台：

```bash
npx skills add <owner>/cursor-novel-writer -a cursor -a qoder -a trae-cn -g -y
```

或 PowerShell：`.\platforms\install.ps1 -Global`

## Skills（8 个）

| Skill | 用途 |
| --- | --- |
| `story-init` | 立项、目录、story bible |
| `character-management` | 人物与关系 |
| `worldbuilding` | 世界观与规则 |
| `plot-structure` | 大纲、伏笔矩阵 |
| `chapter-writing` | 逐章写作、快照 |
| `novel-review` | graphify + 编辑审稿 |
| `novel-export` | EPUB 导出 |
| `novel-marketing` | 简介 / 宣传文案（可选） |

## CLI（与 IDE 同等能力）

```bash
pip install -r requirements.txt

# 新建项目
python engine/novel_cli.py init --title "雾港来信" --premise "..." --output ./my-novel

# 状态 / 审稿 / 导出（--project 可在子命令前或后）
py -3 engine/novel_cli.py --project ./my-novel status
py -3 engine/novel_cli.py status --project ./my-novel
py -3 engine/novel_cli.py review --project ./my-novel
py -3 engine/novel_cli.py export --format epub --project ./my-novel
```

## Graphify

完整一致性需要 [graphify-novel](https://github.com/Anshler/graphify-novel) CLI。
未安装时 bridge 会降级为 offline 索引。

```bash
python engine/scripts/graphify_bridge.py --project ./my-novel init --premise "..."
python engine/scripts/graphify_bridge.py review --chapter chapters/01_*.md --project ./my-novel
```

## 项目结构

```text
my-novel/
├── story.md
├── task_plan.md
├── canon/progress.json
├── characters/
├── worldbuilding/
├── plot/
├── chapters/
└── graphify-out/
```

## 与 cursor-novel-video 衔接

章节 Markdown 路径 `chapters/*.md` 作为视频项目输入。
见 [cursor-novel-video](../cursor-novel-video/README.md)。

## License

MIT
