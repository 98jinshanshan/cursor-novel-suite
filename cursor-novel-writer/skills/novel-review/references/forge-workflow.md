# Forge 审稿工作流（zencoder-novel-engine 风格）

多人格分阶段审稿，最后合成修订计划。**不要**一次让 Agent 扮演所有角色。

Persona 详细 prompt：[personas/](./personas/)

---

## 阶段 1：硬校验（blocker）

**Format** 小节（先于 Blockers 填写）：对照 [chapter-format.md](../../chapter-writing/references/chapter-format.md)

- `# 第N章`、章首章尾 `---`、`（第N章完）`
- `voice-brief` 为 `continuous`（默认）时：任何 `## 一/二/三` 或单独一行「一」「二」「三」→ **blocker**

对照 postwriter 清单，任一失败即 **blocker**：

- POV 与 `story.md` 一致
- 时间线与 `plot/timeline.md` 无矛盾
- 人物位置/能力与上一章一致
- 未违反 `worldbuilding/systems/` 规则
- 伏笔矩阵状态正确

输出：`reviews/chNN-review.md` 顶部 **Blockers** 小节。

**Gate：** 存在 blocker → 禁止阶段 4–5 与导出。

---

## 阶段 2：人格轮审（warn / nit）

按序运行，每人格单独一节（读对应 persona 文件）：

| Persona | 文件 | 关注点 |
| --- | --- | --- |
| **Ghostlight** | [ghostlight.md](./personas/ghostlight.md) | 读者困惑、pacing |
| **Lumen** | [lumen.md](./personas/lumen.md) | 结构、弧线、钩子 |
| **Sable** | [sable.md](./personas/sable.md) | 用词、重复（初轮，非 de-AI 全表） |

---

## 阶段 3：Forge 合成

1. 合并三份输出，去重
2. 分为：**必须改（blocker）** / **建议改（warn）** / **可选（nit）**
3. 给出 **分轮修订计划**（先结构后字句，最多 2 轮）

---

## 阶段 4：去 AI 味（Pipeline Phase 7）

1. 读 `canon/voice-brief.md`
2. 按 [deai-checklist.md](./deai-checklist.md) 全表检查
3. 以 **Sable** persona 输出 **De-AI** 小节 + 行级修改
4. 执行 surgical edits（用户未要求不得全文重写）

---

## 阶段 5：再验证（Pipeline Phase 8）

1. 重跑阶段 1 硬校验
2. 重跑 **Ghostlight** 冷读
3. 若仍有 blocker 或 deai ❌ → 回到阶段 4（**全循环最多 2 次**）
4. 通过后标记 `task_plan.md` Phase 7–8 为 `[x]`

---

## Graphify 集成点

- 审稿前：`graphify_bridge.py review --chapter ...`
- 多章后：`update --from-chapters`
- 关系查询：`query --from "A" --to "B"`

```bash
python skills/novel-review/scripts/graphify_bridge.py --project . review --chapter chapters/01_*.md
```

---

## 禁止

- 未过 blocker 直接进入润色全文
- 人格输出互相矛盾时不做 synthesis 直接改稿
- 跳过阶段 5 直接导出 EPUB
