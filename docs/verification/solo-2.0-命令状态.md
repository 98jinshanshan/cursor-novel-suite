# SOLO 2.0 — 命令状态（只复制，不读长文）

**你当前进度（侯府春深 `novel-f5026010`）：**

| 状态 | 内容 | 你的情况 |
| --- | --- | --- |
| 0 | 同步 + 验收 | ✅ 已完成 |
| 1 | 引擎验收 | ✅ 状态1通过 |
| 2 | 新书冒烟 | ⏭ 跳过（书已存在） |
| 2-pre | 第1章格式+审稿 | ⚠️ **未验收**（你发过《入府》全文，曾判格式 blocker） |
| 3 | 写第2章《暗格》 | ✅ 已落盘 |
| **任务单** | **同步规范 → 去 ch1–3 一二三 → 写 ch4** | 👉 **先 PowerShell，再发任务单** |
| 4 | demo 视频 | 可选 |

**路径：** 书在 SOLO 盘用 `G:\SOLO小说项目\cursor-novel-writer`；与 Cursor 统一请改开 **`G:\CURSOR`**（见下文双路径说明）。

**格式变更（2026-06）：** 单章 **禁止** 章内「一、二、三」/`## 一`；默认 **continuous** 连贯正文。

---

## ① 你在 PowerShell 执行（拉最新规范 + Skills）

```powershell
cd G:\SOLO小说项目\cursor-novel-writer
$env:NOVEL_SUITE_ROOT = (Get-Location).Path
powershell -File platforms/solo-sync.ps1 -UseZip -Agents trae-cn
```

（若 SOLO 与 Cursor 要同一本书：把 `cd` 改成 `G:\CURSOR`，并在 Cursor 用 `robocopy` 同步 `novel-f5026010` 后再写。）

---

## ② 复制下面【一整块】发给 SOLO

**规则：** `chapter_structure: continuous` — **禁止** 章内 `一/二/三` 或 `## 一/二/三`；只保留 `# 第N章`、`---`、连贯段落、`（第N章完）`。

```text
【侯府春深·任务单·连贯章体】novel-f5026010
根：G:\SOLO小说项目\cursor-novel-writer
禁止：章内出现 一/二/三 或 ## 一/二/三（删标题保留剧情，用空行衔接）
禁止：C:\Users\Public\；草稿 novels/novel-f5026010/chapters/.drafts/

━━ 0 环境 ━━
cd G:\SOLO小说项目\cursor-novel-writer
$env:NOVEL_SUITE_ROOT = (Get-Location).Path
$env:PYTHONPATH = (Join-Path $env:NOVEL_SUITE_ROOT "src")
Read：.trae/skills/chapter-writing/references/chapter-format.md（最新：默认 continuous）

━━ 1 锁定文风契约 ━━
Read/更新：novels/novel-f5026010/canon/voice-brief.md
确保有：chapter_structure | continuous
若无则补上，并写明：单章禁止一二三小节

━━ 2 改前三章（去章内小节，剧情不动）━━
依次处理：chapters/01_入府.md、02_暗格.md、03_*.md（若尚无第3章则跳过 03）
每章须：# 第N章：<标题>、首尾 ---、（第N章完）；删除所有 ## 一/二/三 及单独一行「一」「二」「三」
改完后自检：全文搜索无「^## [一二三]$」、无「^一二三$」

━━ 3 写第4章（连贯，不得用一二三）━━
Read：chapter-writing/SKILL.md、task_plan.md 第4章、chapters/03_*.md 或 02_暗格.md（以已有最新章为准）
Read：canon、plot/foreshadowing.md
Write 草稿：novels/novel-f5026010/chapters/.drafts/ch04.md
  仅 # 第4章：<task_plan标题> + 连贯正文 + （第4章完），禁止章内小节标题
py -3 -m novel_suite.cli writer chapter draft --project novels/novel-f5026010 --chapter 4 --title "<task_plan第4章标题>" --input novels/novel-f5026010/chapters/.drafts/ch04.md --json

━━ 4 简要验收 ━━
Write：reviews/ch01-review.md、ch02-review.md（若缺）及 ch04 对应 review 的 ## Format 段
Format 须写：continuous，无章内一二三 ✅

━━ 完成口令 ━━
2+3 成功 → 回复：任务单完成（ch1-3已去小节、ch4落盘）
```

**双路径：** Cursor 在 `G:\CURSOR` 看不到书时，任务单执行完后在 Cursor 终端：

```powershell
robocopy "G:\SOLO小说项目\cursor-novel-writer\novels\novel-f5026010" "G:\CURSOR\novels\novel-f5026010" /E
```

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

## 状态 3｜写第 N 章（通用，continuous）

草稿 `novels/<slug>/chapters/.drafts/ch0<N>.md`：**禁止**章内 `一/二/三`；须 `# 第N章`、连贯段落、`（第N章完）`。见文档顶部 **② 任务单**。

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
① solo-sync → ② 任务单（去 ch1–3 小节 + 写 ch4 连贯）→ robocopy 到 G:\CURSOR（可选）
```

详见 [solo-2.0-test-commands.md](./solo-2.0-test-commands.md)、[chapter-format.md](../../cursor-novel-writer/skills/chapter-writing/references/chapter-format.md)。
