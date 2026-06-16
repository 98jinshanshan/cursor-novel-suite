---
name: chapter-writing
description: |
  Write chapters from outline with canon consistency, self-check, and Story Bible snapshot.
  Use for 写下一章、继续写、chapter write, 续写, draft chapter.
license: MIT
metadata:
  author: cursor-novel-writer
  version: "1.1.0"
---

# Chapter Writing

Fuses story-skills chapter workflow + Novel Master snapshots + novel-skill Chinese format.

## Node Execution Contract (NEC)

**执行前必读：** [references/node-dispatch.md](./references/node-dispatch.md)。落盘章节 + `canon/snapshots/chNN-after.md` +
`phase-5.completion.json`；对话框仅摘要。

## Project Resolution（P4）

**Before writing:** confirm active novel:

```bash
python engine/novel_cli.py active
```

All paths below are relative to **`novels/<slug>/`** (or explicit `--project`).

**Never** write to repo root or another novel's folder.

## Pre-write Context Load

1. `canon/project.json`, `story.md`, `task_plan.md`, `plot/foreshadowing.md`
2. **`canon/voice-brief.md`**（Phase 4，含 platform_target）
3. `characters/`, relevant `worldbuilding/`
4. Previous chapter file if exists
5. Optional: `python skills/chapter-writing/scripts/graphify_bridge.py --project . query --character "<name>"`

## Chapter Structure

**格式规范（必读）：**

- [references/chapter-format.md](./references/chapter-format.md) — 文件层结构
- [references/chinese-prose-layout.md](./references/chinese-prose-layout.md) — **中文叙事排版（段首 `　　`、对话 `“”`）**

- **禁止**正文顶格像 Markdown/README；**禁止**章内「一、二、三」小节。
- 写前必读 `voice-brief`：`chapter_structure: continuous`、`prose_layout: cn-fiction-indent`。

File: `chapters/NN_章节标题.md`

```markdown
# 第3章：雨夜访客

---

　　连贯叙事：每段段首两个全角空格。

　　“对话独立成段，”他说，“同样缩进。”

---

（第3章完）
```

Target: `story.md` → `words_per_chapter`（**CJK 汉字**，`chapter_format_lint` 统计）；默认约 3500–4500。勿与平台「日更 4000」混淆 —
[PLATFORM-LENGTH-AND-NORMS.md](../../docs/standards/PLATFORM-LENGTH-AND-NORMS.md)。

**落盘自检：** 文件层齐全；叙事段以 `　　` 开头；无顶格正文块、无一二三小节。

## Writing Checklist

- [ ] 五感描写至少两处
- [ ] 对话有潜台词
- [ ] 伏笔矩阵中本章条目已处理
- [ ] 未违反 `worldbuilding/systems/` 硬规则
- [ ] 章末钩子

## Post-write

1. Update `task_plan.md` progress and `canon/progress.json`
2. Update `chapters/_index.md`
3. **Snapshot file** (required): copy [templates/snapshot-chapter.md](../../templates/snapshot-chapter.md) →
`canon/snapshots/chNN-after.md`
4. Run review:

   ```bash
   python engine/novel_cli.py review --chapter chapters/NN_*.md --project <novels/slug>
   ```

## Revision drafts（验证阶段）

- 验证/去 AI 改稿 → write to `chapters/.drafts/NN_标题.md` only
- After review pass: `python engine/novel_cli.py promote NN_标题.md --project <novels/slug>`

## Editor Personas (optional pass)

From zencoder-novel-engine — ask user if they want:

- **Ghostlight**: 读者初读感受
- **Lumen**: 结构诊断
- **Sable**: 语句润色

Use `novel-review` skill for full editorial pass.

## Sprint 7 新增

- 雪花法大纲：`novel_suite.writer.snowflake.run_snowflake(topic)` 生成 4 步递进大纲（Agent 调用 LLM 填充每步）
- 角色卡生成：`novel_suite.writer.character_gen.extract_character(text, name)` 从正文提取角色设定
- 格式化输出：`format_snowflake_output()` 生成可读 Markdown 大纲
