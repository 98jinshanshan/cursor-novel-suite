# Forge 审稿工作流（zencoder-novel-engine 风格）

多人格分阶段审稿，最后合成修订计划。**不要**一次让 Agent 扮演所有角色。

---

## 阶段 1：硬校验（blocker）

对照 postwriter 清单，任一失败即 **blocker**：

- POV 与 `story.md` 一致
- 时间线与 `plot/timeline.md` 无矛盾
- 人物位置/能力与上一章一致
- 未违反 `worldbuilding/systems/` 规则

输出：`reviews/chNN-review.md` 顶部 **Blockers** 小节。

---

## 阶段 2：人格轮审（warn / nit）

按序运行，每人格单独一节：

| Persona | 关注点 | 输出格式 |
| --- | --- | --- |
| **Ghostlight** | 读者是否困惑、信息是否过早/过晚 | 3–5 条读者问题 |
| **Lumen** | 结构、节奏、本章是否推动弧线 | 修订清单（优先级） |
| **Sable** | 用词、重复、对话标签 | 行级建议（引用原文片段） |

---

## 阶段 3：Forge 合成

1. 合并三份输出，去重
2. 分为：**必须改（blocker）** / **建议改（warn）** / **可选（nit）**
3. 给出 **分轮修订计划**（先结构后字句，最多 2 轮）

---

## Graphify 集成点

- 审稿前：`graphify_bridge.py review --chapter ...`
- 多章后：`update --from-chapters`
- 关系查询：`query --from "A" --to "B"`

Skill 脚本（Option A）：

```bash
python skills/novel-review/scripts/graphify_bridge.py --project . review --chapter chapters/01_*.md
```

---

## 禁止

- 未过 blocker 直接进入润色全文
- 人格输出互相矛盾时不做 synthesis 直接改稿
