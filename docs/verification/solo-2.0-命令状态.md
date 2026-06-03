# SOLO 2.0 — 命令状态（只复制，不读长文）

按顺序做：**状态 0（你）→ 状态 1（发给 SOLO）→ 状态 2（发给 SOLO）**。  
每段从 `---` 到 `---` 整段复制。

---

## 状态 0｜你在 SOLO 电脑 PowerShell 执行（只做一次）

工作区必须是 **monorepo 根**（有 `.novel-suite-root`），不要只开 `cursor-novel-writer` 子文件夹。

```powershell
# 以本机为准：cd 到含 .novel-suite-root 的目录（常见 G:\SOLO小说项目\cursor-novel-writer，不是 cursor-novel-suite）
cd G:\SOLO小说项目\cursor-novel-writer
$env:NOVEL_SUITE_ROOT = (Get-Location).Path
powershell -File platforms/solo-sync.ps1 -UseZip -Agents trae-cn
pip install -e .
powershell -File platforms/final-verify.ps1
```

**SOLO 环境常见例外（仍可做状态 1）：**

| 步骤 | 失败原因 | 是否阻塞状态 1 |
| --- | --- | --- |
| `pip install -e .` | 沙箱无 `_socket` | 否 → 用下面「状态 1 SOLO」里的 `py -3 -m novel_suite.cli` |
| `final-verify.ps1` | 无 `.git` / 无 `npx` | 否 → 用 doctor + pytest 代替 |
| `solo-sync` patch 报错 | chapter-writing 幽灵目录 | 否 → 修好 skills 且 doctor 15/15 即可 |

**状态 0 通过（SOLO 简化签收）：** `suite doctor` 全绿 + `pytest -m "not ffmpeg"` 约 **99 passed**（你当前已满足）。

### 状态 0 每一行在干什么（含 Skills 更新）

| 你敲的命令 | 实际做了什么 |
| --- | --- |
| `cd` + `$env:NOVEL_SUITE_ROOT` | 进入套件根并告诉引擎「根目录在哪」 |
| **`solo-sync.ps1 -UseZip -Agents trae-cn`** | 见下方「solo-sync 展开」 |
| `pip install -e .` | 安装 **2.0 统一 CLI** `novel-suite`（`solo-sync` 里的 patch **不会**做这一步） |
| `final-verify.ps1` | **2.0 发布级验收**：全仓 `pytest` + pyright + markdownlint（比 solo-sync 末尾的 pytest 更严） |

**solo-sync 展开（一条命令里已包含 Skills 更新）：**

1. **拉新代码**：`-UseZip` → `zip-refresh.ps1` 从 GitHub 下最新包（保留 `novels/`、`intel/`、`.trae/` 等）
2. **patch-update**（自动调用）：
   - `install-skills.ps1 -Agents trae-cn` → 技能 junction 到 **`.trae/skills/`**
   - `pip install -r` writer / video / dev 依赖
   - `suite doctor`（含检查 Phase0 技能 `novel-market-scan`）
   - `pytest`（writer + video，`-m "not ffmpeg"`）

**结论：** Skills 更新**已经包含在** `solo-sync` 里，不需要再单独敲 `install-skills.ps1`；若你只想刷新技能、不拉 zip，可单独执行：

```powershell
powershell -File platforms/install-skills.ps1 -Agents trae-cn
```

**通过（完整机）：** `Patch update complete` + `final-verify` → `OK: all checks passed`。  
**通过（SOLO 机）：** 上表「简化签收」两项已绿即可进入状态 1。

---

## 状态 1｜复制下面整段 → 粘贴到 SOLO Agent 聊天框（引擎验收）

### 状态 1 SOLO 版（`novel-suite` 命令不存在时用这段）

```text
【Novel Suite 2.0 — 状态1 SOLO 引擎验收】
工作区根目录含 .novel-suite-root（本机例如 G:\SOLO小说项目\cursor-novel-writer）。
状态0已通过：suite doctor 15/15，pytest 99 passed。pip install -e . 若失败不要重试，用下面命令1b。

命令1a（若终端能识别 novel-suite）：
novel-suite doctor --core-only --json

命令1b（若无 novel-suite 命令，在 monorepo 根执行）：
$env:PYTHONPATH = (Join-Path $env:NOVEL_SUITE_ROOT "src")
py -3 -m novel_suite.cli doctor --core-only --json

命令2（若状态0已跑过且 99 passed，可汇报「命令2跳过-已验收」否则执行）：
py -3 -m pytest -m "not ffmpeg" -q

命令3：
py -3 cursor-novel-writer/engine/scripts/nec_cursor_smoke.py

命令4：
py -3 cursor-novel-video/engine/scripts/nec_video_smoke.py

JSON：整段 stdout 可 json.loads。命令3 gaps 为空。全部通过后回复：状态1通过
```

### 状态 1 标准版（本机已 pip install -e . 时用）

```text
【Novel Suite 2.0 — 状态1 引擎验收】
工作区必须是 monorepo 根（含 .novel-suite-root），且已 pip install -e .。
请在本机终端依次执行，每步汇报 exit code；失败贴完整 stderr。
JSON 命令：整段 stdout 必须能 json.loads，不要截取「首个 {」。

命令1：
novel-suite doctor --core-only --json

命令2：
py -3 -m pytest -m "not ffmpeg" -q

命令3：
py -3 cursor-novel-writer/engine/scripts/nec_cursor_smoke.py

命令4：
py -3 cursor-novel-video/engine/scripts/nec_video_smoke.py

通过标准：
- 命令1：code 为 OK 或 SUCCESS
- 命令2：约 99 passed, 1 deselected
- 命令3：gaps 为空数组
- 命令4：无 ERROR
全部通过后回复：状态1通过
```

**可选（本机有 FFmpeg 时，另开一轮发给 SOLO）：**

```text
【Novel Suite 2.0 — 状态1b 视频 pytest】
py -3 -m pytest cursor-novel-video/tests -m ffmpeg -q
通过：1 passed。回复：状态1b通过
```

---

## 状态 2｜复制下面整段 → 粘贴到 SOLO Agent（Phase0→立项→门控）

扫榜后 SOLO 会问你选哪个 concept；你回复 concept 文件名后再让它继续。

```text
【Novel Suite 2.0 — 状态2 新书冒烟】
工作区 monorepo 根，已 pip install -e .。每步 json.loads 整段 stdout，汇报 code、message、artifacts。

命令A：
novel-suite writer scan --demo --period week --json
→ 列出可选 concept 路径，等我回复「用 intel/concepts/某某.md」

（我确认 concept 后执行命令B，把下面三处占位符改成我给的值）
命令B：
novel-suite writer init --title "雾港试书" --premise "一封没有寄件人的信改变了一切" --concept intel/concepts/<我确认的文件名>.md --json
→ 记下 details.slug

命令C（把 <slug> 换成命令B的 slug）：
novel-suite writer gate --phase 1 --project novels/<slug> --json

全部通过后回复：状态2通过，slug=...
```

---

## 状态 3｜复制下面整段 → 粘贴到 SOLO Agent（写第二章，真书续写）

**适用：** 状态 1 已通过；书目已有第一章（如 `novels/novel-f5026010/chapters/01_入府.md`），本次写 **第 2 章**，不要重复写第 1 章。

```text
【Novel Suite 2.0 — 状态3 写第二章（续写侯府春深）】
工作区 monorepo 根。项目 slug：novel-f5026010（路径 novels/novel-f5026010）。

步骤：
1) Read .trae/skills/chapter-writing/SKILL.md
2) Read 已有第一章：novels/novel-f5026010/chapters/01_入府.md
3) Read canon：novels/novel-f5026010/canon/concept-brief.md、voice-brief.md、progress.json
4) 按 SKILL 写第2章正文，保存到 C:\Users\Public\ch02.md（勿覆盖 01_入府.md）
   格式必读 chapter-writing/references/chapter-format.md：须 # 第2章、## 一/二/三、（第2章完），禁止纯文本「一」「二」行

命令（无 novel-suite 时用命令B，在根目录先设 PYTHONPATH=...\src）：
命令A：
novel-suite writer chapter draft --project novels/novel-f5026010 --chapter 2 --title "<第2章标题>" --input C:\Users\Public\ch02.md --json

命令B：
$env:NOVEL_SUITE_ROOT = "G:\SOLO小说项目\cursor-novel-writer"
$env:PYTHONPATH = (Join-Path $env:NOVEL_SUITE_ROOT "src")
py -3 -m novel_suite.cli writer chapter draft --project novels/novel-f5026010 --chapter 2 --title "<第2章标题>" --input C:\Users\Public\ch02.md --json

通过：code OK，artifacts 含 chapters/02_*.md；01_入府.md 未被改动。回复：状态3通过
```

`<第2章标题>` 由你指定（例如「暗流」）；不指定则 SOLO 自拟后与文件名一致。

---

## 状态 4｜复制下面整段 → 粘贴到 SOLO Agent（demo 视频，需 FFmpeg）

```text
【Novel Suite 2.0 — 状态4 视频 job】
命令1：
novel-suite video create-summary --chapter 01_试章.md --project cursor-novel-writer/examples/demo-novel --json
→ 记下 details.job_id

命令2（把 <job_id> 换成上一步）：
novel-suite video run --job <job_id> --json

命令3：
novel-suite video status --job <job_id> --json

通过：status 成功且 artifacts 含 mp4。回复：状态4通过
```

---

## 对照：上次 SOLO 结束 vs 现在

| 上次（1.x） | 现在（2.0 本页） |
| --- | --- |
| `novel_cli.py suite doctor` | 状态0 + 状态1 命令1 `novel-suite doctor` |
| `pytest ...` 约38条 | 状态0 `final-verify`；状态1 命令2 约99条 |
| `intel_scan --demo` + `novel init` | 状态2 命令A/B |
| `pipeline gate` | 状态2 命令C |
| 手工写章 | 状态3 |
| `video_cli summary` | 状态4 |

详细说明见 [solo-2.0-test-commands.md](./solo-2.0-test-commands.md)。
