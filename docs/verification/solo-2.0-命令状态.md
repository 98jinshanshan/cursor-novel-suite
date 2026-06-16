# SOLO 2.0 — 三条复制块（不读长文）

长文说明见 [solo-2.0-test-commands.md](./solo-2.0-test-commands.md)。

**路径：** 把 `G:\CURSOR` 换成你的 Novel Suite 根（含 `.novel-suite-root`）。

---

## ① PowerShell — 同步 + 验收（人工，发版前一次）

```powershell
cd G:\CURSOR
$env:NOVEL_SUITE_ROOT = (Get-Location).Path
powershell -File platforms/solo-sync.ps1 -UseZip -Agents trae-cn
pip install -e .
powershell -File platforms/final-verify.ps1
```

**通过：** 最后一行 `OK: all checks passed`。

---

## ② SOLO 聊天 — 引擎验收（贴整段）

```text
工作区 = Novel Suite 根，已 pip install -e .。
Read AGENTS.md 与 novel-pipeline/SKILL.md。

代为执行并汇报 exit code（失败贴 stderr）：
1) novel-suite doctor --core-only --json
2) py -3 -m pytest -m "not ffmpeg" -q
3) py -3 cursor-novel-writer/engine/scripts/nec_cursor_smoke.py

JSON：stdout 须完整 json.loads，禁止截取「首个 {」。
```

---

## ③ SOLO 聊天 — 写书任务（贴整段，改书名/路径）

```text
按 novel-pipeline 总控执行（先 Read novel-pipeline/SKILL.md）。
根目录：G:\CURSOR
$env:NOVEL_SUITE_ROOT = 根目录

1) novel active（或 --project novels/<slug>）
2) 从 task_plan 当前 Phase 继续；未立项则 Phase 0：
   novel intel scan --period week --fallback-demo → 等我确认 concept → init
3) 每 Phase 结束：pipeline gate --phase N
4) 写章用 chapter-writing；写完 novel-review 审稿

我的目标：[扫榜 / 新开书 / 写下一章 / 审稿 / 导出 EPUB / 做 9:16 视频]
```

---

*每月差距矩阵：`py -3 cursor-novel-writer/engine/novel_cli.py suite gap-diff`*
