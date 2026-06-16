# Novel Suite — Agent 对话入口（主路径）

本仓库是 **Agent Skills 工具包**，不是「只能开终端敲 CLI」的脚本集合。

- **主入口**：各 IDE 的 **Agent 对话窗口**（自然语言触发 Skills）
- **引擎层**：`novel_cli.py` / `video_cli.py`（由 Agent 在后台调用，用户通常无需手敲）

**工作区契约：** 打开 **Novel Suite 根目录**（含 `.novel-suite-root` 与 `cursor-novel-writer/`，路径任意，如 `D:/projects/novel-suite`）。

---

## 默认入口（一句话 — 复制即用）

**除非用户点名单个 Skill，否则一律先 Read `novel-pipeline`，按总控编排 delegate。**

```text
按 novel-pipeline 总控执行。先 Read cursor-novel-writer/skills/novel-pipeline/SKILL.md。
1) novel active（或 --project novels/<slug>）
2) 读 task_plan 当前 Phase；未立项则从 Phase 0 扫榜（novel-market-scan）
3) 每 Phase 结束跑 pipeline gate --phase N；有 blocker 禁止下一阶段
4) 代码/配置改动收尾：final-verify + Final Verification 块

我的目标：[扫榜 / 新开书 / 写下一章 / 审稿 / 导出 / 做视频 — 填一项]
```

| 用户说法 | 路由 |
| --- | --- |
| 全流程 / 写小说 / 开书 / _pipeline_ | 上段话术 → `novel-pipeline` |
| 只扫榜 / 选题 | `novel-market-scan`（仍属 Phase 0） |
| 只写一章 | `chapter-writing` + 完成后 `novel-review` |
| 只导出 / 只视频 | `novel-export` / `video-chapter-summary` |

SOLO 三条复制块：[solo-2.0-命令状态.md](docs/verification/solo-2.0-命令状态.md)

### Session 复盘（压缩后）

```text
整理压缩对话：Read session-retrospect → ingest-pending → 更新问题总表。
逻辑重排：Read session-lifecycle-reorder → 更新 lifecycle-reordered.md。
```

安装压缩前 Hook（用户级，归档到**当前工作区** `docs/audit/session-archives/`）：

```powershell
powershell -File platforms/install-session-hooks.ps1
powershell -File platforms/install-session-skills.ps1 -Agents cursor -AlsoAgents
```

**Reload（必做一次）：** `Ctrl+Shift+P` → 输入 `Reload Window` → 选 **Developer: Reload Window**。

详见 [SESSION-ARCHIVE.md](docs/standards/SESSION-ARCHIVE.md)。

---

## 一次性准备

```bash
# 在 Novel Suite 根目录（含 .novel-suite-root）
npx skills add ./cursor-novel-writer -a cursor -a qoder -a trae-cn -y
npx skills add ./cursor-novel-video -a cursor -a qoder -a trae-cn -y

pip install -r requirements-dev.txt
pip install -r cursor-novel-writer/requirements.txt
pip install -r cursor-novel-video/requirements.txt

py -3 cursor-novel-writer/engine/novel_cli.py suite doctor
```

Windows 也可用：

```powershell
powershell -File platforms/install-skills.ps1 -Agents cursor
powershell -File platforms/patch-update.ps1 -Agents cursor   # git pull 后拉补丁
powershell -File platforms/solo-sync.ps1 -UseZip -Agents trae-cn   # SOLO / 无 git
```

**重要：** Skills 必须装到当前工作区；Option A 脚本依赖完整仓库里的 `engine/scripts/`。  
**Skill 清单与 Phase 0 对照：** [docs/standards/SKILLS-INSTALL.md](docs/standards/SKILLS-INSTALL.md)  
**SOLO 测试端同步：** `platforms/solo-sync.ps1`（`-UseZip` / `-Source G:\CURSOR` / `-UseGit`）→
[solo-clone-checklist.md](docs/verification/solo-clone-checklist.md)

---

## Phase 0 = `novel-market-scan`（无 `phase-0/` 目录）

| 说法 | 实际 |
| --- | --- |
| Phase 0 / 扫榜 / 选题 | Skill **`novel-market-scan`** |
| 引擎命令 | `novel intel scan --period week --fallback-demo` |
| 必装 wrapper | `.trae/skills/novel-market-scan/scripts/intel_scan.py` |

Agent 读技能时**必须先 Read `novel-market-scan`**，再执行 Phase 1+。

### Phase 0 离线 / 联网失败 fallback（P0 契约）

联网不稳定（SSL、超时、零命中）时**不得**跳过 Phase 0。按序降级：

| 步骤 | 命令 / 动作 | 产物 |
| --- | --- | --- |
| 1 | `novel intel scan --period week --fallback-demo` | `intel/radar/YYYY-Www.md` + `*.completion.json` |
| 2 | 仍失败 → `novel intel scan --demo --period week` | 同上（fixture，标 WARN） |
| 3 | 有用户粘贴/自采样本 → `novel intel scan --input ./hits.json` | 同上 |
| 4 | **P0-S2** Agent 补全 `## 平台快照`（见 platform-scan-guide） | 番茄/起点/晋江/盐选表 |
| 5 | 对齐 radar-report-template | 周报复用骨架，只换日期与表格 |

**周报复用：** 复制上周 `intel/radar/YYYY-Www.md` 结构 → 更新 Executive Summary、平台快照表、检索日期；勿从零发明章节。

**`--input` JSON 格式：** `[{"platform":"douyin","title":"…","url":"…","snippet":"…"}, …]`（见
`intel/fixtures/smoke-hits.json`）。

---

## 默认总控 Skill

所有「写小说全流程」请求，优先路由到 **`novel-pipeline`**。

| 阶段 | Delegate Skill | 你在对话里可以说 |
| --- | --- | --- |
| 0 选品 | `novel-market-scan` | 扫榜、本周热门短视频、题材雷达、选题 |
| 1 立项 | `story-init` | 新建小说、开书、立项 |
| 2–3 设定 | `worldbuilding` + `character-management` + `plot-structure` | 补世界观、人物、大纲 |
| 4 文风 | voice-brief | 定文风、平台合规 |
| 5 写作 | `chapter-writing` | 写下一章、续写 |
| 6–8 验证 | `novel-review` | 审稿、查伏笔、去 AI 味 |
| 9 导出 | `novel-export` | 导出 EPUB |
| 视频 | `video-chapter-summary` / `video-scene-drama` | 章节摘要视频、分场景成片 |

---

## 展开话术（按需 — 默认用上文「一句话入口」）

### Phase 0 — 全平台扫榜 → 选题

```text
请读取 novel-market-scan Skill，执行本周全平台短视频热榜扫描：
1) 运行 novel intel scan --period week --fallback-demo
2) 若 stderr 有 WARN/ERROR，按 AGENTS.md「Phase 0 离线 fallback」降级并补 P0-S2 平台快照
3) 展示 intel/radar 当周报告 Top 题材
4) 从 intel/concepts 推荐 Top1，等我确认后再 init
```

### Phase 0→1 — 全流程开书

```text
按 novel-pipeline 从 Phase 0 开始：
先扫榜选题，我确认 concept 后自动 init 到 novels/<slug>，
并执行 pipeline gate --phase 1。
```

### 写作 / 审稿 / 导出

```text
对 active 小说写下一章（chapter-writing），写完后 novel-review 审稿。
```

### NEC-11 审计（格式 / 去 AI / 门控）

```text
读 audit-dispatch-index，对 active 小说最新章依次执行：
1) novel audit format --json
2) novel audit blocker --json（Phase 6）
3) novel audit deai --modes all --json（Phase 7）
把 scan JSON 摘要写入 reviews/chNN-review.md 的 De-AI Scan 节。
```

```text
检查 pipeline 状态；若 gate 通过，导出 EPUB。
```

### 小说 → 视频

```text
把 active 小说最新章节做成 9:16 摘要短视频，加字幕（video-chapter-summary）。
```

---

## 各 IDE 对话入口

| IDE | Skills 目录 | 对话方式 |
| --- | --- | --- |
| **Cursor** | `.agents/skills/`（+ `.cursor/skills/`） | Agent 模式直接说上面话术 |
| **Qoder** | `.qoder/skills/` | Agent 对话；可绑 subagent |
| **TRAE CN / SOLO** | `.trae/skills/` 或 `~/.trae-cn/skills/` | 自然语言或 `#novel-pipeline` |

**不要混淆：** SOLO「上传自定义 Agent」≠ 安装 Skills 目录。两者必须分别配置（见 [docs/verification/trae-cn.md](docs/verification/trae-cn.md)）。

---

## Agent 执行约定

0. 进入 Phase N 前：**Read** 该 Skill 的 `references/node-dispatch.md`（[NEC 契约](docs/standards/NODE-EXECUTION-CONTRACT.md)）
1. 开始任何写入前：`novel active` 或 `--project novels/<slug>`
2. Phase 0 未完成 → 禁止实质写作（`pipeline gate --phase 1`）
3. 有 blocker → 禁止导出（`pipeline gate --phase 9`）
4. 脚本失败时必须展示 stderr，不得假装成功
5. **代码任务收尾：** 运行 `platforms/final-verify.ps1` 或 `final-verify.sh`；
   回复须含 [Final Verification](docs/standards/FINAL-VERIFICATION.md) 块（与 CI `final-verify` job 对齐）

---

## CLI 附录（调试 / CI 用）

用户未要求时，Agent 应优先走对话 + Skill，CLI 仅作引擎调用。

```bash
python cursor-novel-writer/engine/novel_cli.py intel scan --period week
python cursor-novel-writer/engine/novel_cli.py init --title "..." --premise "..." --concept ./intel/concepts/xxx.md
python cursor-novel-writer/engine/novel_cli.py audit format --project novels/<slug> --json
python cursor-novel-writer/engine/novel_cli.py audit deai --project novels/<slug> --modes all --json
python cursor-novel-writer/engine/novel_cli.py pipeline gate --phase 1
python cursor-novel-video/engine/video_cli.py summary --chapter ./novels/<slug>/chapters/01_*.md --subtitles
```

更多触发语：[cursor-novel-writer/skills/novel-pipeline/references/quick-triggers.md](cursor-novel-writer/skills/novel-pipeline/references/quick-triggers.md)
