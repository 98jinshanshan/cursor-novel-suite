# Plot Frameworks（情节框架参考）

按需加载。默认中文通用小说用 **三幕式**；短篇或氛围向可试 **起承转合**。

---

## 三幕式（默认）

| 幕 | 功能 | 典型占比 |
| --- | --- | --- |
| 第一幕 | 日常 → 诱因 → 进入新世界 | ~25% |
| 第二幕 | 试炼、中点反转、一切尽失 | ~50% |
| 第三幕 | 高潮、抉择、新常态 | ~25% |

**输出：** `plot/arcs/<arc-id>.md` 中标注各幕对应章节。

---

## 起承转合（kishotenketsu）

| 段 | 含义 | 写作提示 |
| --- | --- | --- |
| 起 | 介绍情境 | 人物与空间，不必立刻冲突 |
| 承 | 发展、加深 | 事件链延伸 |
| 转 | 意外变化 | 认知或局势转折 |
| 合 | 收束 | 余韵或新平衡 |

适合：悬疑氛围、散文式章节、弱对抗叙事。

---

## Save the Cat（15 节拍，可选）

常用节拍：Opening Image → Theme Stated → Break into Two → Midpoint → All Is Lost → Finale。

**用法：** 在 `task_plan.md` 为每章标注对应节拍名，避免机械填表。

---

## 选型建议

| 类型 | 推荐 |
| --- | --- |
| 悬疑 / 长篇 | 三幕式 |
| 文学 / 短篇 | 起承转合 |
| 商业类型片感 | Save the Cat 辅助 |

---

## 与 deliverables 的映射

1. `plot/arcs/*.md` — 弧级结构
2. `plot/timeline.md` — 时间顺序
3. `plot/foreshadowing.md` — 伏笔矩阵
4. `task_plan.md` — 分章 checklist
