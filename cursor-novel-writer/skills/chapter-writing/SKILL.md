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

File: `chapters/NN_章节标题.md` (e.g. `03_雨夜访客.md`)

```markdown
# 第3章：雨夜访客

---

## 一
[场景：时间地点 + 动作]

## 二
[对话与冲突]

## 三
[转折 + 章末钩子]

---

（第3章完）
```

Target: 3500–5500 字 unless user specifies.

## Writing Checklist

- [ ] 五感描写至少两处
- [ ] 对话有潜台词
- [ ] 伏笔矩阵中本章条目已处理
- [ ] 未违反 `worldbuilding/systems/` 硬规则
- [ ] 章末钩子

## Post-write

1. Update `task_plan.md` progress and `canon/progress.json`
2. Update `chapters/_index.md`
3. **Snapshot file** (required): copy [templates/snapshot-chapter.md](../../templates/snapshot-chapter.md) → `canon/snapshots/chNN-after.md`
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
