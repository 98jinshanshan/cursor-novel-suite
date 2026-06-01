# 雾港来信 — 示例项目（对标 story-skills the-last-ember）

完整度：**3 人物 + 2 地点 + 1 世界观规则 + 1 故事弧 + 1 章**。

| 类型 | 内容 |
| --- | --- |
| 人物 | 陈薇、林默、顾远 → `characters/` |
| 地点 | 雾港档案馆、雾港老码头 → `worldbuilding/locations/` |
| 规则 | 档案封存制度 → `worldbuilding/systems/archive-seal-system.md` |
| 弧 | 匿名信主线 → `plot/arcs/arc-main-letter.md` |
| 章节 | `chapters/01_试章.md` |

## CLI 试跑

```bash
cd cursor-novel-writer
py -3 engine/novel_cli.py export --project examples/demo-novel --format epub
py -3 engine/novel_cli.py review --project examples/demo-novel
```

## 视频试跑

```bash
cd cursor-novel-video
py -3 engine/video_cli.py summary --chapter ../cursor-novel-writer/examples/demo-novel/chapters/01_试章.md --subtitles
```

样片可复制到 `cursor-novel-video/demos/`（见 demos/README.md）。

## Agent 触发

「根据 examples/demo-novel 继续写第 2 章」

**全流程（推荐）：**

「用 novel-pipeline 从 Phase 6 继续 demo-novel：验证、去 AI 味、导出 EPUB」

```bash
py -3 engine/novel_cli.py pipeline status --project examples/demo-novel
```
