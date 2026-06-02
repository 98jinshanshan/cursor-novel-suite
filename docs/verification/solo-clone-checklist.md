# SOLO / TRAE 克隆后安装清单

**适用：** 从 GitHub 下载 zip / clone 到新目录（如 `g:\SOLO小说项目\cursor-novel-suite`）  
**仓库：** <https://github.com/98jinshanshan/cursor-novel-suite>  
**Skill 规范：** [SKILLS-INSTALL.md](../standards/SKILLS-INSTALL.md)

---

## Phase 0 说明（SOLO 易混淆）

- **没有** 名为 `phase-0` 的 Skill 目录。
- **Phase 0 = `novel-market-scan`**（扫榜 / 选题 / `intel scan`）。
- **总控 = `novel-pipeline`**（Phase 0 会 delegate 到 `novel-market-scan`）。
- Agent 扫技能列表时，必须 **Read `novel-market-scan/SKILL.md`**，不能跳过。

---

## 常见错误（SOLO 实测）

| 错误做法 | 后果 |
| --- | --- |
| IDE 只打开 `cursor-novel-writer/` 子目录 | Option A 脚本找不到 `engine/scripts/` |
| 只下载 13 个 `SKILL.md` | 缺 `scripts/intel_scan.py`，Phase 0 CLI 失败 |
| 依赖过期的 `skills-lock.json` | 漏列 `novel-market-scan` / `novel-pipeline`（已 gitignore） |
| 只上传 SOLO Agent、不跑 `install-skills.ps1` | 对话可见 Agent 但「找不到 skill」 |
| 在错误目录跑 `suite doctor` | 报 suite_root FAIL |

**正确：** IDE 工作区 = **含 `.novel-suite-root` 的 monorepo 根**（与 `cursor-novel-writer/`、`cursor-novel-video/` 同级）。

---

## 标准安装（Windows）

```powershell
git clone https://github.com/98jinshanshan/cursor-novel-suite.git
cd cursor-novel-suite

pip install -r requirements-dev.txt
pip install -r cursor-novel-writer/requirements.txt
pip install -r cursor-novel-video/requirements.txt

powershell -File platforms/install-skills.ps1 -Agents trae-cn

py -3 cursor-novel-writer/engine/novel_cli.py suite doctor
```

zip 下载：解压后进入**含 `.novel-suite-root` 的那一层**再打开 IDE。

---

## 开发 → SOLO 测试闭环

| 角色 | 路径 | 每次 push 后 |
| --- | --- | --- |
| **开发（Cursor）** | `G:\CURSOR` | `git push origin main` |
| **测试（SOLO）** | 例如 `G:\SOLO小说项目\…`（monorepo 根） | 见下方 **solo-sync** |

SOLO **不必**重 clone；**不必**读 `G:\CURSOR`（SOLO 对 g:\ 写入常受限）。

```powershell
# SOLO 测试端（无 git 时默认 HTTP zip）
powershell -File platforms/solo-sync.ps1 -UseZip -Agents trae-cn

# 同机且可读开发目录时（可选）
powershell -File platforms/solo-sync.ps1 -Source G:\CURSOR -Agents trae-cn

# 已有 .git 且网络通
powershell -File platforms/solo-sync.ps1 -UseGit -Agents trae-cn
```

同步后跑 **方案 A** 验收（下文「SOLO Agent 对话模板」）。

### SOLO 实测对照（避免假绿）

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 无 `solo-sync.ps1` / `patch-update.ps1` | 旧 zip（如 934e7af） | `solo-sync.ps1 -UseZip` |
| `suite doctor` OK 但缺 platforms/ | doctor 旧版未检 sync 工具 | 同步到 `2026.06.02-sync` 后重跑 doctor |
| pytest video 3 失败 | 旧版 `novel_bind` | 同步最新 main |
| `intel scan` 联网失败 | DuckDuckGo 不可用 | `intel scan --demo`（离线 fixture） |
| Agent 用 mock JSON 冒充 Phase 0 | 未用官方 `--demo` | 改用 CLI `--demo`，输出含 WARN |

---

## 补丁式更新（已克隆 SOLO 项目）

在 **Novel Suite 根目录** 一键执行：

```powershell
powershell -File platforms/patch-update.ps1 -Agents trae-cn
```

等价于：`git pull` → 重装 Skills junction → pip → `suite doctor` → Phase 0 文件检查 → pytest（32 passed）。

**无 git 时（SOLO 推荐）：** 一条命令同步 GitHub 最新并验收：

```powershell
powershell -File platforms/solo-sync.ps1 -UseZip -Agents trae-cn
```

等价于：HTTP 下载 main.zip → 覆盖代码（保留 `novels/`、`intel/`）→ install-skills → pip → doctor → pytest（**32 passed**）。

手动分步：`platforms/zip-refresh.ps1` → `patch-update.ps1 -SkipPull`。

**最低版本：** `suite-version=2026.06.03-nec`（含 NEC smoke、node sync、intel --demo）。

---

## 全流程 smoke（Agent 对话）

| 步骤 | 输入 | 预期 |
| --- | --- | --- |
| 0 | `请运行 novel suite doctor` | 核心 OK；`.trae/skills` 13 个 |
| **0b** | `请先 Read novel-market-scan，再 intel scan --period week` | **`intel/radar/*.md`**（Phase 0） |
| 1 | `#novel-pipeline 显示 pipeline status` | Phase 列表含 Phase 0 |
| 2 | `把 demo 第1章做成 9:16 summary 视频` | `tmp/video_jobs/.../output/*.mp4` |

SOLO System Prompt：[solo-agent-prompt.md](../../cursor-novel-writer/platforms/trae/solo-agent-prompt.md)

---

## SOLO Agent 对话模板

可直接复制到 SOLO Agent 对话窗口。建议先 **方案 A 第 1–2 步**，Phase 0 通过后再做 3–4 步；省事时用 **方案 B** 一条总任务。

### 使用前确认（说一次即可）

```text
请确认当前 IDE 工作区是 Novel Suite 根目录（含 .novel-suite-root、cursor-novel-writer/、cursor-novel-video/），不是只打开 cursor-novel-writer 子文件夹。若不是，请先提示我改工作区再继续。
```

### 方案 A：分步对话（推荐）

#### 第 1 步 — 同步最新（原「补丁更新」）

```text
请在本工作区执行 SOLO 同步（不要只读 SKILL.md）：
1) powershell -File platforms/solo-sync.ps1 -UseZip -Agents trae-cn
   （若无 solo-sync.ps1，说明版本过旧，先用 zip-refresh.ps1 或 HTTP 拉 main.zip）
2) 把通道选择、exit code、suite doctor、pytest 摘要原样贴出
3) 若有 FAIL，给出修复命令，不要跳过
```

预期：`solo-sync` 成功、`.trae/skills` 13 个、pytest **32 passed**、`doctor` 含 sync_tooling OK。

#### 第 2 步 — Phase 0 专项

```text
Phase 0 没有 phase-0/ 目录，对应 Skill 是 novel-market-scan。请：
1) Read .trae/skills/novel-market-scan/SKILL.md（不要只看目录名）
2) 确认存在 .trae/skills/novel-market-scan/scripts/intel_scan.py
3) 运行 py -3 cursor-novel-writer/engine/novel_cli.py intel paths
4) 运行 py -3 cursor-novel-writer/engine/novel_cli.py intel scan --period week
   （联网失败则：intel scan --demo --period week，并说明 WARN 离线模式）
5) 列出 intel/radar/ 最新报告路径，并摘要 Top3 题材
若未 Read novel-market-scan 就执行 scan，请说明并重来。
```

预期：生成 `intel/radar/YYYY-Www.md`，Agent 明确提到 **novel-market-scan**（不是虚构的 phase-0 skill）。

#### 第 3 步 — 总控与门控

```text
请 Read novel-pipeline 的 SKILL.md，然后：
1) py -3 cursor-novel-writer/engine/novel_cli.py pipeline status --project cursor-novel-writer/examples/demo-novel
2) py -3 cursor-novel-writer/engine/novel_cli.py pipeline gate --phase 1 --project cursor-novel-writer/examples/demo-novel
3) 用表格说明 Phase 0–9 哪些已完成、下一 Phase 是什么
```

#### 第 4 步 — 视频 + 绑定（可选）

```text
请 Read video-chapter-summary 的 SKILL.md，然后：
1) 对 demo 第 1 章生成 9:16 summary 视频（加字幕）
2) 检查 storyboard.json 里是否有 novel 字段（slug/demo-novel）
3) 给出 output mp4 完整路径
若缺 FFmpeg，说明并只做到 storyboard/TTS 阶段。
```

#### 第 5 步 — 验收汇报

```text
请按下面清单做最终验收表（每项 OK/FAIL + 证据路径）：
- 工作区含 .novel-suite-root
- .trae/skills 共 13 个（含 novel-market-scan、novel-pipeline）
- novel-market-scan/scripts/intel_scan.py 存在
- suite doctor 核心项全 OK
- Phase 0 intel scan 有 radar 产出
- pipeline status / gate phase 1 通过
- pytest 32 passed（若你跑了 patch-update）
- 说明 Phase 0 对应 novel-market-scan，不是 phase-0 目录
```

### 方案 B：一条总任务

```text
你是 Novel Suite 助手。请严格按顺序执行并汇报（必须代为运行命令，不要只给命令让我手敲）：

【0】确认工作区为 Novel Suite 根（.novel-suite-root）。
【1】powershell -File platforms/solo-sync.ps1 -UseZip -Agents trae-cn
【2】Read novel-market-scan/SKILL.md → intel scan --demo（或联网 scan）→ 展示 radar Top3
【3】Read novel-pipeline/SKILL.md → pipeline status + gate --phase 1（demo-novel）
【4】可选：demo 第1章 9:16 summary 视频加字幕
【5】输出验收表：13 skills、Phase0=novel-market-scan、doctor、pytest、产物路径

约束：
- Phase 0 必须先 Read novel-market-scan，禁止虚构 phase-0 skill
- 命令失败必须贴 stderr，不得假装成功
- 参考 docs/standards/SKILLS-INSTALL.md 与 docs/verification/solo-clone-checklist.md
```

### 纠偏话术（Agent 跳过 Phase 0 时）

```text
你跳过了 Phase 0。仓库里没有 phase-0/ 目录，Phase 0 的唯一 Skill 是 novel-market-scan。
请先 Read .trae/skills/novel-market-scan/SKILL.md 全文，再执行 intel scan。
在此之前不要进入 story-init 或写章。
```

### 成功标准

| 项 | 通过标志 |
| --- | --- |
| 同步 | `solo-sync.ps1 -UseZip` 无报错 |
| Phase 0 | Agent **读过** `novel-market-scan`，且有 `intel/radar/*.md` |
| 总控 | 能解释 Phase 0→1 门控，且 `pipeline gate --phase 1` OK |
| 技能 | `.trae/skills/novel-market-scan/scripts/intel_scan.py` 存在 |
| 测试 | pytest **32 passed**（patch-update 默认会跑） |

**小提示：** SOLO 自定义 Agent 请从最新
[solo-agent-prompt.md](../../cursor-novel-writer/platforms/trae/solo-agent-prompt.md)
粘贴 System Prompt（含「Phase 0 = novel-market-scan 优先」）。

---

## 自动化测试（可选）

```powershell
py -3 -m pytest cursor-novel-writer/tests cursor-novel-video/tests -m "not ffmpeg" -q
```

**通过标准：** **32 passed**（2026-06 起）。

---

## 目录结构速查

```text
cursor-novel-suite/          ← IDE 打开这一层
├── .novel-suite-root
├── .trae/skills/
│   └── novel-market-scan/   ← Phase 0（含 scripts/intel_scan.py）
├── cursor-novel-writer/skills/
├── platforms/
│   ├── install-skills.ps1
│   ├── solo-sync.ps1        ← SOLO 同步入口（zip / mirror / git）
│   ├── zip-refresh.ps1
│   └── patch-update.ps1
├── intel/fixtures/smoke-hits.json  ← intel scan --demo
└── AGENTS.md
```
