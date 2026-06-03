# SOLO 话术模板：从选题到第一章

**适用：** TRAE / SOLO Agent 对话（PowerShell 已由你或 Agent 代跑）  
**前提：** `suite-version ≥ 2026.06.03-nec`，`.trae/skills` 13 个已装  
**工作区：** Novel Suite 根（含 `.novel-suite-root`；你当前可为 `...\cursor-novel-writer`）

**不要**把下面中文说明贴进 PowerShell；只贴进 **SOLO 聊天框**。

---

## 使用前填好（复制前改一次）

```text
【本书参数 — 请改成你的】
- 选定题材：intel/concepts/2026-W23-01-novel-289d0565.md  （或 ②③，写清编号）
- 书名：雾港来信
- 一句话 premise：雾港出现可验证的「记忆残影」，女主追查三年前沉船真相。
- 目标平台：番茄（或 起点 / 晋江）
```

---

## 0 — 工作区确认（一句）

```text
请确认工作区为 Novel Suite 根（.novel-suite-root、platforms/、cursor-novel-writer/、novels/、intel/）。
确认后不要重复跑 solo-sync，除非我明确要求。
```

---

## 1 — Phase 0 选题（novel-market-scan）

```text
Phase 0 = novel-market-scan（无 phase-0/ 目录）。请：

1) Read .trae/skills/novel-market-scan/SKILL.md 与 references/node-dispatch.md
2) 若 intel/radar/ 本周尚无报告：运行
   py -3 cursor-novel-writer/skills/novel-market-scan/scripts/intel_scan.py --demo
   （联网可用则：py -3 cursor-novel-writer/engine/novel_cli.py intel scan --period week）
3) 展示 Top3 题材摘要 + 三个 concept 路径，等我确认选哪一个（①②③）
4) 我确认后：把选定 concept 标为 approved，并写入立项用 concept-brief 要点（不编造未读内容）

对话框只报 Top3 + 路径；全文在 intel/radar/*.md。
```

**你回复示例（选题材后）：**

```text
我选 concept ①，按该 concept 立项。
```

---

## 2 — Phase 1 立项（story-init）

```text
我已在 Phase 0 选定 concept。请 Read story-init 的 SKILL.md 与 node-dispatch.md，然后：

1) 代跑：py -3 cursor-novel-writer/engine/novel_cli.py novel list
2) 根据我提供的书名与 premise，起草 story.md 要点（先对话确认再落盘）
3) 代跑 init（路径按你工作区调整，concept 用我选的 intel/concepts/*.md）：
   py -3 cursor-novel-writer/engine/novel_cli.py init ^
     --title "雾港来信" ^
     --premise "雾港出现可验证的记忆残影，女主追查三年前沉船真相。" ^
     --concept intel/concepts/2026-W23-01-novel-289d0565.md
4) 代跑：pipeline gate --phase 1 --project novels/<实际slug>
5) 代跑：node sync --phase 1 --project novels/<实际slug>
6) node validate --phase 1

汇报：novels/<slug>/ 路径、story.md、phase-1.completion.json 是否 complete。
```

---

## 3 — Phase 2 世界观 + 人物（worldbuilding + character-management）

```text
请 Read worldbuilding 与 character-management 的 SKILL.md 及各自 node-dispatch.md，对 novels/<slug>：

1) 至少 1 个地点 + 1 条规则/系统（worldbuilding/）
2) 至少 2 张人物卡（characters/），关系双向一致
3) 代跑：novel relations check --project novels/<slug>
4) pipeline gate --phase 3
5) node sync --phase 2 && node validate --phase 2

汇报落盘路径与 gate 结果。
```

---

## 4 — Phase 3 大纲（plot-structure）

```text
请 Read plot-structure 的 SKILL.md 与 node-dispatch.md，对 novels/<slug>：

1) plot/arcs/ 至少 1 个弧光文件
2) plot/foreshadowing.md（含第1章相关伏笔）
3) 给出第1章分章要点（起承转合，不写完正文）
4) pipeline gate --phase 4
5) node sync --phase 3 && node validate --phase 3

汇报第1章大纲要点 + 路径。
```

---

## 5 — Phase 4 文风契约（voice-brief）

```text
请 Read templates/voice-brief.md，为 novels/<slug> 填写 canon/voice-brief.md（含 ## 发表平台）。

代跑：
- pipeline gate --phase 5 --project novels/<slug>
- node sync --phase 4 && node validate --phase 4

对话框摘要：POV、时态、平台、禁用项各一句。
```

---

## 6 — Phase 5 写第一章（chapter-writing）

```text
请 Read chapter-writing 的 SKILL.md 与 node-dispatch.md，写第 1 章：

1) novel use <slug>（或全程 --project novels/<slug>）
2) 写作前对照：voice-brief、foreshadowing、相关人物卡
3) 产出 chapters/01_<标题>.md（2000–4000 字，强钩子开篇，符合 voice-brief）
4) 产出 canon/snapshots/ch01-after.md（Story Bible 快照）
5) 更新 canon/progress.json
6) pipeline gate --phase 6
7) node sync --phase 5 && node validate --phase 5

对话框：章名、字数、本章钩子一句；正文只在 chapters/，对话不贴全文。
```

---

## 7 — 可选：第1章审稿（novel-review，建议）

```text
请 Read novel-review 的 SKILL.md，对第1章做 Phase 6 验证（不润色全文）：

1) 产出 reviews/ch01-review.md（含 ## Blockers、## De-AI 占位）
2) Blockers 若无则写 (none)
3) node sync --phase 6

汇报 open blockers 数量。
```

---

## 8 — 收尾验收表

```text
请输出「选题→第一章」验收表：

| Phase | Skill | 关键产物 | OK/FAIL |
| 0 | novel-market-scan | intel/radar + concept 选定 | |
| 1 | story-init | novels/<slug>/story.md | |
| 2 | worldbuilding+character | ≥2 人物 + 世界观 | |
| 3 | plot-structure | arcs + foreshadowing + 第1章要点 | |
| 4 | voice-brief | canon/voice-brief.md | |
| 5 | chapter-writing | chapters/01_*.md + snapshot | |

并列出所有 pipeline gate（1–6）与 node validate 结果。
```

---

## 一条总任务（省事版）

```text
你是 Novel Suite 写作助手。从 Phase 0 到第1章，严格按 NEC：每 Phase 先 Read 对应 .trae/skills/<name>/SKILL.md 与 node-dispatch.md，代跑 CLI，产物落盘。

【参数】concept=①，书名=雾港来信，premise=（见上），平台=番茄。

顺序：Phase0 选题确认 → init 立项 → Phase2 人物世界观 → Phase3 大纲+第1章要点 → Phase4 voice-brief → Phase5 写 chapters/01_*.md + snapshot → 可选 ch01-review。

禁止：虚构 phase-0 skill；mock 雷达；只给命令不执行；对话贴整章正文。

每步汇报：slug、路径、gate/validate exit code。参考 docs/verification/solo-phase0-to-ch01-dialogue.md
```

---

## 纠偏话术

| 现象 | 发送 |
| --- | --- |
| 没选题就 init | 请先完成 Phase 0 并等我选 concept ①②③。 |
| 没大纲就写章 | 请先完成 plot-structure 与 voice-brief。 |
| 跳过 gate | 每 Phase 结束必须 pipeline gate，失败贴 stderr。 |
| 正文只在聊天里 | 章节必须写入 chapters/01_*.md。 |

---

## 相关文档

- [solo-nec-dialogue.md](./solo-nec-dialogue.md) — 引擎 smoke
- [solo-clone-checklist.md](./solo-clone-checklist.md) — 安装同步
- [NEC-smoke-matrix.md](./NEC-smoke-matrix.md) — 三端矩阵
