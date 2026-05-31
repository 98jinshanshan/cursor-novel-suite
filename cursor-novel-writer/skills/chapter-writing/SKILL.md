---
name: chapter-writing
description: |
  Write chapters from outline with canon consistency, self-check, and Story Bible snapshot.
  Use for 写下一章、继续写、chapter write, 续写, draft chapter.
license: MIT
metadata:
  author: cursor-novel-writer
  version: "1.0.0"
---

# Chapter Writing

Fuses story-skills chapter workflow + Novel Master snapshots + novel-skill Chinese format.

## Pre-write Context Load

1. `story.md`, `task_plan.md`, `plot/foreshadowing.md`
2. `characters/`, relevant `worldbuilding/`
3. Previous chapter file if exists
4. Optional: `python skills/chapter-writing/scripts/graphify_bridge.py --project . query --character "<name>"`

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
3. Run review:

   ```bash
   python skills/chapter-writing/scripts/graphify_bridge.py --project . review --chapter chapters/NN_*.md
   ```

4. Emit **Story Bible 快照** (unless user says 不需要):

```markdown
## 快照 — 第N章后
- 状态变更：...
- 新伏笔 / 回收：...
- 下一章钩子：...
```

## Editor Personas (optional pass)

From zencoder-novel-engine — ask user if they want:

- **Ghostlight**: 读者初读感受
- **Lumen**: 结构诊断
- **Sable**: 语句润色

Use `novel-review` skill for full editorial pass.
