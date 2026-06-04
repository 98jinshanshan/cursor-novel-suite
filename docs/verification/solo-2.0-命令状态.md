# SOLO 2.0 — 命令状态（只复制，不读长文）

**你当前进度（侯府春深 `novel-f5026010`）：**

| 状态 | 内容 | 你的情况 |
| --- | --- | --- |
| 0 | 同步 + 验收 | ✅ 已完成 |
| 1 | 引擎验收 | ✅ 状态1通过 |
| **任务单** | **中文排版 ch1–3 + 写 ch4** | 👉 **先 ① 再 ②** |

**路径：** `G:\SOLO小说项目\cursor-novel-writer`（与 Cursor 统一可改 `G:\CURSOR`）。

**格式（2026-06）：** 正文每段段首 **`　　`（两个全角空格）**；禁止顶格像 README；禁止章内「一二三」。见 `chinese-prose-layout.md`。

---

## ① PowerShell

```powershell
cd G:\SOLO小说项目\cursor-novel-writer
$env:NOVEL_SUITE_ROOT = (Get-Location).Path
powershell -File platforms/solo-sync.ps1 -UseZip -Agents trae-cn
```

---

## ② 整段发给 SOLO

```text
【侯府春深·任务单·中文排版】novel-f5026010
根：G:\SOLO小说项目\cursor-novel-writer
Read 必读：.trae/skills/chapter-writing/references/chinese-prose-layout.md
禁止：顶格正文；禁止章内 一/二/三 或 ## 一/二/三；禁止 C:\Users\Public\

━━ 0 环境 ━━
cd G:\SOLO小说项目\cursor-novel-writer
$env:NOVEL_SUITE_ROOT = (Get-Location).Path
$env:PYTHONPATH = (Join-Path $env:NOVEL_SUITE_ROOT "src")

━━ 1 voice-brief ━━
更新 novels/novel-f5026010/canon/voice-brief.md：
  chapter_structure | continuous
  prose_layout | cn-fiction-indent

━━ 2 改 ch1–ch3（只改排版，不改剧情）━━
文件：chapters/01_入府.md、02_暗格.md、03_*.md（无03则跳过）
保留：# 第N章、首尾 ---、（第N章完）
删除：## 一/二/三、单独一行「一」「二」「三」
正文：每个自然段段首加两个全角空格「　　」；对话用 “ ” 并独立成段
禁止：顶格大段、Markdown 列表 - 叙事
自检：随机抽 5 段，均应以 　　 开头

━━ 3 写 ch4 ━━
Read：chapter-writing/SKILL.md、task_plan 第4章、上一章、canon、foreshadowing.md
Write：novels/novel-f5026010/chapters/.drafts/ch04.md（按 chinese-prose-layout）
py -3 -m novel_suite.cli writer chapter draft --project novels/novel-f5026010 --chapter 4 --title "<task_plan第4章标题>" --input novels/novel-f5026010/chapters/.drafts/ch04.md --json

━━ 4 Format 验收 ━━
reviews：prose_layout=cn-fiction-indent ✅、continuous ✅

━━ 完成 ━━
回复：任务单完成（ch1-3已排版、ch4落盘）
```

**Cursor 同步（可选）：**

```powershell
robocopy "G:\SOLO小说项目\cursor-novel-writer\novels\novel-f5026010" "G:\CURSOR\novels\novel-f5026010" /E
```

详见 [chinese-prose-layout.md](../../cursor-novel-writer/skills/chapter-writing/references/chinese-prose-layout.md)。
