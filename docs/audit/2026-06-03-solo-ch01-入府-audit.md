# 审稿审计 — SOLO 试写第1章《入府》（novel-f5026010）

**日期：** 2026-06-03  
**范围：** 正文质量（撰稿人视角）+ 工作流合规（NEC / chapter-writing / novel-review）  
**对照：** `chapter-writing` SKILL、`deai-checklist`、`forge-workflow` Phase 1

---

## 执行摘要

| 维度 | 评级 | 说明 |
| --- | --- | --- |
| 文学完成度 | B+ | 古言宅斗开篇扎实，钩子明确（私印、柳氏、暗格） |
| 格式合规 | **C-（blocker）** | 缺 `#` / `##` / `---` / `（第1章完）`；`一/二/三` 为节拍但未按 Markdown 落盘 |
| NEC 后处理 | **未做** | 未见 snapshot、review、gate phase 6、progress 更新（测试章可补跑） |

**结论：** 正文可保留为草稿素材；**须先格式规范化 + 走 review 再视为 Phase 5 完成。**

---

## 一、「一、二、三」分段说明

**不是写作事故。** 工作流 **故意** 用三章内节拍（起—承—转）：

- **一：** 入府、见柳氏、月例与拂衣院安排  
- **二：** 拂衣院勘察、酉时请安、东边小门  
- **三：** 夜探地砖、沈印、印面磨薄悬念  

与 `examples/demo-novel/chapters/01_试章.md` 及 `chapter-writing/references/chapter-format.md` 一致。

**当前问题：** SOLO 产出为**纯文本** `一` `二` `三`，未写成 `## 一`，属 **格式未按 SKILL 落盘**，不是体裁错误。

---

## 二、Ghostlight（读者冷读）

### 优点

- 侯府礼制、器物（门钉、缂丝、沉香）有画面，非空泛「古代背景」  
- 沈知意 POV 稳定，内心算计与表面恭顺分层清楚  
- 章末钩子强：生母私印 + 印面人为磨薄，与柳氏「哪有老实的」形成张力  

### 建议（warn）

- 「知意心中 / 知意心里」类句式略密，第二章起可多用动作代替  
- 柳氏「像打量瓷器」略熟梗，可保留一次，避免全书重复  
- 二、三之间时间跳切（酉时→夜深）清晰，可在「三」首句加半句时间锚（如「过了子时」）减突兀感  

---

## 三、Lumen（结构）

| 检查项 | 结果 |
| --- | --- |
| 章内三节拍是否各有关键事件 | ✅ |
| 章末钩子 | ✅ 私印 + 磨薄 |
| 与 Phase 0 concept / voice 对齐 | ⚠️ 未对照本仓 `canon/voice-brief.md`（SOLO 机本地） |
| 字数 | ⚠️ 约 3200–3800 字量级，偏低缘合格线，可接受试章 |

---

## 四、Sable / De-AI（抽样）

| 项 | 结果 |
| --- | --- |
| 段首「然而/不过」堆叠 | ✅ 未见明显堆叠 |
| 「不禁/不由得」 | ✅ 未滥用 |
| 眼神/目光同场景 | ✅ 约 2 次，合规 |
| 章末总结式说教 | ✅ 以悬念收束，非说教 |
| 翻译腔模板句 | ✅ 少见 |
| 平台模板化段落 | ⚠️ 宅斗入门桥段常见，靠后续章节差异化 |

---

## 五、工作流 Blockers（必须修）

1. **Markdown 结构：** 按 `chapter-writing/references/chapter-format.md` 重排落盘。  
2. **NEC 产出缺失：**  
   - `canon/snapshots/ch01-after.md`  
   - `reviews/ch01-review.md`（含 `## Format`、`## De-AI`）  
   - `canon/progress.json` / `chapters/_index.md` 更新  
3. **Gate：** `pipeline gate --phase 6`（或 `novel-suite writer gate --phase 6`）未跑则不算写完一章。

---

## 六、推荐修复稿结构（节选）

```markdown
# 第1章：入府

---

## 一

永宁侯府的正门漆着朱红……

## 二

拂衣院在侯府东北角……

## 三

夜深了，拂衣院里静得只听见虫鸣……

---

（第1章完）
```

正文句段可不变，仅补标题与分隔符。

---

## 七、后续动作（SOLO / 人工）

1. 将现有正文套入 §六 模板，覆盖 `novels/novel-f5026010/chapters/01_入府.md`（先备份）。  
2. 运行 `novel-review` 或 `novel_cli.py review --chapter chapters/01_入府.md`。  
3. 写 `ch01-after` 快照后再开状态 3 写第 2 章。
