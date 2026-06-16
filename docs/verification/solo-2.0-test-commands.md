# SOLO / TRAE — Novel Suite 2.0 测试命令（重设计）

> **只想复制命令、不想读长文 → 用 [solo-2.0-命令状态.md](./solo-2.0-命令状态.md)（状态 0→4，整段粘贴即可）。**

**版本：** 2026-06-03（对齐 `main` ≥ `ba5883e`、`novel-suite==2.0.0`）  
**前置：** [solo-clone-checklist.md](./solo-clone-checklist.md) ·
[smoke-checklist.md](../../skills/openclaw-novel-suite/references/smoke-checklist.md)

**原则：** 人工在 PowerShell 跑确定性验收；SOLO Agent 对话跑 **JSON 主链路** + 必要时 legacy `novel_cli.py`（NEC `node sync` 等）。

---

## 1. 上次 SOLO 结束时常用的命令（Legacy，1.x 文档）

对话与文档里典型组合如下（**仍可用**，但 2.0 验收以右侧「推荐」为准）：

| 场景 | 上次命令（Legacy） |
| --- | --- |
| 同步到 SOLO 机 | `powershell -File platforms/solo-sync.ps1 -UseZip -Agents trae-cn` |
| 引擎自检 | `py -3 cursor-novel-writer/engine/novel_cli.py suite doctor --agents trae-cn` |
| 自动化测试 | `py -3 -m pytest cursor-novel-writer/tests cursor-novel-video/tests -m "not ffmpeg" -q`（当时约 **38** passed） |
| NEC 烟测 | `py -3 cursor-novel-writer/engine/scripts/nec_cursor_smoke.py` |
| Phase 0 扫榜 | `py -3 cursor-novel-writer/skills/novel-market-scan/scripts/intel_scan.py --demo` 或 `novel_cli.py intel scan` |
| 立项 | `py -3 cursor-novel-writer/engine/novel_cli.py init --title ... --concept intel/concepts/....md` |
| 门控 | `py -3 cursor-novel-writer/engine/novel_cli.py pipeline gate --phase N --project novels/<slug>` |
| 写章 | Skill + 手工落盘 `chapters/01_*.md`（或 promote） |
| 真书试跑（曾暂停） | `novels/novel-f5026010`（侯府春深）— 非标准 NEC 短路径 |

**上次对话里 OpenClaw/验收链（Cursor 侧已跑通）：**  
`doctor → scan → init → gate → chapter draft`（当时逐步改为 `novel-suite writer * --json`）。

---

## 2. 2.0 对照：推荐替换什么

| 能力 | 2.0 推荐（Agent 可代跑） | Legacy（保留） |
| --- | --- | --- |
| 安装 CLI | `pip install -e .`（monorepo 根） | — |
| 一键验收 | `powershell -File platforms/final-verify.ps1` | 分散 pytest + doctor |
| 健康 | `novel-suite doctor --core-only --json` | `novel_cli.py suite doctor --agents trae-cn` |
| 扫榜 | `novel-suite writer scan --demo --json` | `intel scan` / `intel_scan.py --demo` |
| 立项 | `novel-suite writer init --title ... --premise ... --concept ... --json` | `novel init ...` |
| 门控 | `novel-suite writer gate --phase N --project ... --json` | `pipeline gate --phase N` |
| 写章 | `novel-suite writer chapter draft ... --json` | 手工 + `promote` |
| 导出 | `novel-suite writer export --format markdown\|epub --json` | `novel export --format epub` |
| 视频 job | `novel-suite video create-summary` → `run` → `status --json` | `video_cli.py summary` |
| NEC 节点清单 | — | `novel node sync/validate --phase N`（demo-novel） |
| OpenClaw 编排 | Read `skills/openclaw-novel-suite/SKILL.md` | Read 各 `.trae/skills/*/SKILL.md` |

**pytest 预期：** `99 passed, 1 deselected`（`not ffmpeg`）；视频管线另跑 `-m ffmpeg` → `1 passed`。

---

## 3. SOLO 人工准备（PowerShell，一次性 / 发版前）

在 **monorepo 根**（含 `.novel-suite-root`，不要只开 `cursor-novel-writer/`）：

```powershell
cd G:\SOLO小说项目\cursor-novel-suite   # 或本机 G:\CURSOR
$env:NOVEL_SUITE_ROOT = (Get-Location).Path

# 从 GitHub 拉 2.0（无 git 用 zip）
powershell -File platforms/solo-sync.ps1 -UseZip -Agents trae-cn

pip install -e .
powershell -File platforms/final-verify.ps1
```

**通过标准：** `final-verify` → `OK: all checks passed`。

**发版前清理本地垃圾（避免误判）：** 见 [RELEASE-READINESS.md](../RELEASE-READINESS.md)（`novels/*` 测试书目、`video_jobs/*`）。

---

## 4. SOLO Agent — 引擎层验收（贴进聊天框）

```text
请确认工作区为 Novel Suite 根，且已 pip install -e .。
读取 .novel-suite-root 的 suite-version（应含 2026.06 或更新）。

代为执行并汇报 exit code（失败必须贴 stderr）：

1) novel-suite doctor --core-only --json
2) py -3 -m pytest -m "not ffmpeg" -q
3) py -3 cursor-novel-writer/engine/scripts/nec_cursor_smoke.py
4) py -3 cursor-novel-video/engine/scripts/nec_video_smoke.py

JSON 规则：整段 stdout 必须能 json.loads，禁止截取「首个 {」。
pytest 预期约 99 passed, 1 deselected。
nec_cursor_smoke 的 gaps 必须为空数组。
```

**可选（视频机有 FFmpeg）：**

```powershell
py -3 -m pytest cursor-novel-video/tests -m ffmpeg -q
```

---

## 5. SOLO Agent — Phase 0→1 最小真链路（2.0 JSON）

参数先改：concept 路径、书名、premise。

```text
【2.0 新书冒烟 — 请代跑并 json.loads 整段 stdout】

1) novel-suite writer scan --demo --period week --json
   → 汇报 details.themes 或 concept 路径，等我确认选一个 concept 文件

2) 我确认后：
   novel-suite writer init --title "<书名>" --premise "<梗概>" `
     --concept intel/concepts/<file>.md --json
   → 记下 details.slug

3) novel-suite writer gate --phase 1 --project novels/<slug> --json

4) （可选）novel-suite writer export --project novels/<slug> --format markdown --json
   仅当 gate phase 9 已通过或你只做 demo 导出测试

每步汇报：code、message、artifacts 路径；error 时列 next_actions。
写章仍用 .trae/skills/chapter-writing：先 Read SKILL.md，正文写 /tmp/ch01.md 再：
   novel-suite writer chapter draft --project novels/<slug> --chapter 1 --title "<章名>" --input /tmp/ch01.md --json
```

**Legacy NEC 仍建议在 demo 上跑一遍（与 Cursor CI 对齐）：**

```text
对 cursor-novel-writer/examples/demo-novel，phase=1..9：
  py -3 cursor-novel-writer/engine/novel_cli.py node sync --phase N --project ...
  py -3 cursor-novel-writer/engine/novel_cli.py node validate --phase N
```

---

## 6. SOLO Agent — 视频 job（2.0，需 FFmpeg）

```text
1) novel-suite video create-summary `
     --chapter 01_试章.md `
     --project cursor-novel-writer/examples/demo-novel --json
   → 记下 details.job_id，status 应为 pending

2) novel-suite video run --job <job_id> --json
3) novel-suite video status --job <job_id> --json
   → 成功：VIDEO_RUN_OK / VIDEO_STATUS_OK，artifacts 含 *.mp4

一步版：create-summary 加 --run --json（同机需 FFmpeg）。
```

---

## 7. SOLO System Prompt 补充段（贴在 Agent 末尾）

```text
【Novel Suite 2.0 — 2026-06-03】
- 优先：novel-suite writer|video|doctor ... --json（OpenClaw 契约见 skills/openclaw-novel-suite/）。
- 写书仍须 Read .trae/skills/<phase>/SKILL.md；Phase 0 = novel-market-scan（无 phase-0/ 目录）。
- NEC 节点 sync/validate 仍用：py -3 cursor-novel-writer/engine/novel_cli.py node sync|validate ...
- 禁止 mock 雷达；离线用 writer scan --demo --json。
- stdout 解析：整段 json.loads，legacy 提示只在 details.legacy_output。
```

完整模板仍见 [solo-agent-prompt.md](../../cursor-novel-writer/platforms/trae/solo-agent-prompt.md)（建议人工合并上一段）。

---

## 8. 与旧文档的关系

| 文档 | 用途 |
| --- | --- |
| 本文 | **2.0 命令总表**（测试首选） |
| [solo-nec-dialogue.md](./solo-nec-dialogue.md) | NEC 对话细节（需将 pytest 38→99、补 novel-suite） |
| [solo-phase0-to-ch01-dialogue.md](./solo-phase0-to-ch01-dialogue.md) | 选题→第一章话术（CLI 逐步改为本文 §5） |
| [solo-clone-checklist.md](./solo-clone-checklist.md) | 安装 / solo-sync |
| [smoke-checklist.md](../../skills/openclaw-novel-suite/references/smoke-checklist.md) | 发布前人工签收 |

---

## 9. 快速对照：上次 vs 现在

```text
上次结束（典型）:
  solo-sync -UseZip → suite doctor → pytest(≈38) → nec_smoke
  → intel_scan --demo → novel init → pipeline gate → 手工写章

现在 SOLO 2.0 推荐:
  solo-sync -UseZip → pip install -e . → final-verify.ps1
  → novel-suite doctor --json → pytest(99)
  → writer scan/init/gate --json → chapter draft --json → export --json
  → video create-summary → run → status --json
  → （可选）legacy node sync/validate + nec_smoke
```
