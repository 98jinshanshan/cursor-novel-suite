# SOLO 2.0 — 命令状态（只复制，不读长文）

**你当前进度（侯府春深 `novel-f5026010`）：**

| 状态 | 内容 | 你的情况 |
| --- | --- | --- |
| 0 | 同步 + 验收 | ✅ 已完成 |
| 1 | 引擎验收 | ✅ 状态1通过 |
| 2 | 新书冒烟 | ⏭ 跳过（书已存在） |
| 2-pre | 第1章格式+审稿 | ⚠️ **未验收**（你发过《入府》全文，曾判格式 blocker） |
| 3 | 写第2章《暗格》 | ✅ 已落盘 |
| **任务单** | **先收尾 ch1 → 审 ch2 → gate6 → 写 ch3** | 👉 **现在只发最上方一整块** |
| 4 | demo 视频 | 可选 |

**路径：** `G:\SOLO小说项目\cursor-novel-writer`（不是 `cursor-novel-suite`）。

---

## 👉 只复制下面【一整块】发给 SOLO（一条任务单，不要分 A/B）

**你干什么：** 全选复制 → 粘贴 SOLO → 等一句 **`任务单完成`**。中间不要你再发第二条。

**起点：** 第 1 章《入府》是你专门发来审计的（一二三格式、NEC 未做完）；第 2 章已写。  
**本单顺序：** **先收尾第 1 章** → 审第 2 章 → gate 6 → 写第 3 章。（不能跳过第 1 章。）

```text
【侯府春深·任务单】novel-f5026010
根：G:\SOLO小说项目\cursor-novel-writer
禁止：删改 01/02 剧情正文（仅允许格式套壳、review 列 must-fix）
禁止：C:\Users\Public\；草稿用 novels/.../chapters/.drafts/

━━ 0 环境 ━━
cd G:\SOLO小说项目\cursor-novel-writer
$env:NOVEL_SUITE_ROOT = (Get-Location).Path
$env:PYTHONPATH = (Join-Path $env:NOVEL_SUITE_ROOT "src")

━━ 1 第1章《入府》验收（你曾发全文审计的问题，必做）━━
Read：.trae/skills/chapter-writing/references/chapter-format.md
Read：novels/novel-f5026010/chapters/01_入府.md
检查：是否有 # 第1章：入府、---、## 一/二/三（非单独一行「一」）、（第1章完）
若缺 → 只补 Markdown 结构，句段尽量不动
Read：.trae/skills/novel-review/SKILL.md + forge-workflow + deai-checklist
Read：novels/novel-f5026010/canon/voice-brief.md
Write：novels/novel-f5026010/reviews/ch01-review.md
  必含 ## Format、## Blockers、## De-AI、## Ghostlight；Format 须说明「一二三=章内节拍非事故」
若无 canon/snapshots/ch01-after.md → 按模板补写
ch01 有 Blocker → 停，回复「任务单失败：ch1-blocker」

━━ 2 审第2章《暗格》━━
Read：novels/novel-f5026010/chapters/02_暗格.md
Write：novels/novel-f5026010/reviews/ch02-review.md（同上四小节）
ch02 有 Blocker → 停，回复「任务单失败：ch2-blocker」

━━ 3 gate ━━
py -3 cursor-novel-writer/engine/novel_cli.py pipeline gate --phase 6 --project novels/novel-f5026010
失败 → 「任务单失败：gate6」

━━ 4 写第3章 ━━
Read：chapter-writing/SKILL.md、task_plan.md、02_暗格.md、canon、foreshadowing.md
Write：novels/novel-f5026010/chapters/.drafts/ch03.md（# 第3章、## 一/二/三、（第3章完））
py -3 -m novel_suite.cli writer chapter draft --project novels/novel-f5026010 --chapter 3 --title "<task_plan第3章标题>" --input novels/novel-f5026010/chapters/.drafts/ch03.md --json

━━ 完成口令 ━━
1+2+3+4 全成功 → 只回复：任务单完成（ch1已验收、ch2已审、gate6过、ch3落盘）
```

**下一轮：** 任务单改为「验收 ch3 → 审 ch3 → gate → 写 ch4」。

---

## 状态 0｜你在 SOLO 电脑 PowerShell（已完成可跳过）

```powershell
cd G:\SOLO小说项目\cursor-novel-writer
$env:NOVEL_SUITE_ROOT = (Get-Location).Path
powershell -File platforms/solo-sync.ps1 -UseZip -Agents trae-cn
pip install -e .
powershell -File platforms/final-verify.ps1
```

SOLO 机：`pip install -e .` / `final-verify` 失败不阻塞；用状态 1 SOLO 版 + doctor + pytest 签收。

---

## 状态 1 SOLO 版（已完成可跳过）

```text
【Novel Suite 2.0 — 状态1 SOLO 引擎验收】
（略，见历史记录。通过后回复：状态1通过）
```

---

## 状态 2｜新书冒烟（无书时才用）

```text
【Novel Suite 2.0 — 状态2 新书冒烟】
（novel-f5026010 已存在则跳过）
```

---

## 状态 2-pre｜修第1章格式（写第2章前，已完成可跳过）

```text
【修第1章格式】
Read .trae/skills/chapter-writing/references/chapter-format.md
只改 novels/novel-f5026010/chapters/01_入府.md：补 # 第1章、---、## 一/二/三、（第1章完），正文尽量不动。
完成后回复：第1章格式已修
```

---

## 状态 3｜写第 N 章（通用模板）

**第 2 章已完成。** 写第 3 章时用下面模板，改 4 处：`3`、`第3章标题`、`ch03.md`、`02_暗格.md`。

**SOLO 实测注意：**

- **不要**写 `C:\Users\Public\`（常无权限）→ 草稿放 `novels/novel-f5026010/chapters/.drafts/ch03.md`
- `--title` 必须与 `task_plan.md` 里该章标题一致（第2章为 `暗格`）
- 落盘前必读 `chapter-format.md`（`## 一/二/三`，禁止纯文本「一」）
- `--input` 用 SOLO 实际保存路径（与草稿路径相同即可）

```text
【Novel Suite 2.0 — 状态3 写第<N>章】
项目：novels/novel-f5026010（侯府春深）。

步骤：
1) Read .trae/skills/chapter-writing/SKILL.md
2) Read .trae/skills/chapter-writing/references/chapter-format.md
3) Read novels/novel-f5026010/task_plan.md（确认本章标题与情节点）
4) Read 上一章：novels/novel-f5026010/chapters/02_暗格.md
5) Read canon：concept-brief.md、voice-brief.md、progress.json、plot/foreshadowing.md
6) 写第<N>章草稿 → novels/novel-f5026010/chapters/.drafts/ch0<N>.md
   须含 # 第<N>章：<标题>、## 一/二/三、（第<N>章完）；对照 voice-brief 禁用词

命令（monorepo 根）：
$env:NOVEL_SUITE_ROOT = "G:\SOLO小说项目\cursor-novel-writer"
$env:PYTHONPATH = (Join-Path $env:NOVEL_SUITE_ROOT "src")
py -3 -m novel_suite.cli writer chapter draft `
  --project novels/novel-f5026010 `
  --chapter <N> `
  --title "<与task_plan一致的章名>" `
  --input novels/novel-f5026010/chapters/.drafts/ch0<N>.md `
  --json

通过：code 为 CHAPTER_DRAFT_OK；生成 chapters/0<N>_*.md；上一章文件未改动；
      有 canon/snapshots/ch0<N>-after.md；progress 已更新。
回复：状态3通过，章号=<N>
```

**写第 3 章时复制版（已填好占位）：**

```text
【Novel Suite 2.0 — 状态3 写第3章】
项目：novels/novel-f5026010。第1–2章已存在，禁止改动 01_入府.md、02_暗格.md。

步骤：Read chapter-writing SKILL + chapter-format.md + task_plan.md +
  chapters/02_暗格.md + canon（concept/voice/progress）+ plot/foreshadowing.md
草稿：novels/novel-f5026010/chapters/.drafts/ch03.md（格式同 chapter-format.md）
章名：从 task_plan.md 第3章标题填写，填到下面 --title 与正文 # 第3章：

$env:NOVEL_SUITE_ROOT = "G:\SOLO小说项目\cursor-novel-writer"
$env:PYTHONPATH = (Join-Path $env:NOVEL_SUITE_ROOT "src")
py -3 -m novel_suite.cli writer chapter draft `
  --project novels/novel-f5026010 --chapter 3 --title "<第3章标题>" `
  --input novels/novel-f5026010/chapters/.drafts/ch03.md --json

回复：状态3通过，章号=3
```

---

## 状态 5｜审稿第2章（👉 现在发给 SOLO）

```text
【Novel Suite 2.0 — 状态5 审稿第2章】
项目：novels/novel-f5026010。第2章文件：chapters/02_暗格.md（状态3已通过，勿重写正文除非 review 要求）。

步骤：
1) Read .trae/skills/novel-review/SKILL.md
2) Read .trae/skills/novel-review/references/forge-workflow.md
3) Read .trae/skills/novel-review/references/deai-checklist.md
4) Read novels/novel-f5026010/canon/voice-brief.md
5) 对照 chapter-format.md 检查 02_暗格.md，写入 reviews/ch02-review.md
   须含小节：## Format、## Blockers、## De-AI、## Ghostlight（各条 ✅/❌）
6) 无 Blocker 后执行：
$env:NOVEL_SUITE_ROOT = "G:\SOLO小说项目\cursor-novel-writer"
py -3 cursor-novel-writer/engine/novel_cli.py pipeline gate --phase 6 --project novels/novel-f5026010

全部无 blocker 且 gate phase 6 通过 → 回复：状态5通过
```

---

## 状态 4｜demo 视频（可选）

```text
【Novel Suite 2.0 — 状态4 视频 job】
（demo-novel 试章，与侯府春深无关；需 FFmpeg）
novel-suite video create-summary --chapter 01_试章.md `
  --project cursor-novel-writer/examples/demo-novel --json
→ run --job <id> → status --job <id>
回复：状态4通过
```

---

## 流程（真书续写）

```text
0 → 1 → [2-pre] → 3(第2章✅) → 5(审稿第2章) → 3(第3章) → 5(审稿第3章) → …
```

详见 [solo-2.0-test-commands.md](./solo-2.0-test-commands.md)、[chapter-format.md](../../cursor-novel-writer/skills/chapter-writing/references/chapter-format.md)。
