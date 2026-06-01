# Novel Suite — Agent 对话入口（主路径）

本仓库是 **Agent Skills 工具包**，不是「只能开终端敲 CLI」的脚本集合。

- **主入口**：各 IDE 的 **Agent 对话窗口**（自然语言触发 Skills）
- **引擎层**：`novel_cli.py` / `video_cli.py`（由 Agent 在后台调用，用户通常无需手敲）

**工作区契约：** 打开 **Novel Suite 根目录**（含 `.novel-suite-root` 与 `cursor-novel-writer/`，路径任意，如 `D:/projects/novel-suite`）。

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
powershell -File platforms/install-skills.ps1
powershell -File platforms/patch-update.ps1   # git clone 后拉补丁
powershell -File platforms/solo-sync.ps1 -UseZip -Agents trae-cn   # SOLO / 无 git
```

**重要：** Skills 必须装到当前工作区；Option A 脚本依赖完整仓库里的 `engine/scripts/`。  
**Skill 清单与 Phase 0 对照：** [docs/standards/SKILLS-INSTALL.md](docs/standards/SKILLS-INSTALL.md)  
**SOLO 测试端同步：** `platforms/solo-sync.ps1`（`-UseZip` / `-Source G:\CURSOR` / `-UseGit`）→ [solo-clone-checklist.md](docs/verification/solo-clone-checklist.md)

---

## Phase 0 = `novel-market-scan`（无 `phase-0/` 目录）

| 说法 | 实际 |
| --- | --- |
| Phase 0 / 扫榜 / 选题 | Skill **`novel-market-scan`** |
| 引擎命令 | `novel intel scan --period week` |
| 必装 wrapper | `.trae/skills/novel-market-scan/scripts/intel_scan.py` |

Agent 读技能时**必须先 Read `novel-market-scan`**，再执行 Phase 1+。

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

## 推荐对话话术（复制即用）

### Phase 0 — 全平台扫榜 → 选题

```text
请读取 novel-market-scan Skill，执行本周全平台短视频热榜扫描：
1) 运行 novel intel scan --period week
2) 展示 intel/radar 当周报告 Top 题材
3) 从 intel/concepts 推荐 Top1，等我确认后再 init
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

1. 开始任何写入前：`novel active` 或 `--project novels/<slug>`
2. Phase 0 未完成 → 禁止实质写作（`pipeline gate --phase 1`）
3. 有 blocker → 禁止导出（`pipeline gate --phase 9`）
4. 脚本失败时必须展示 stderr，不得假装成功

---

## CLI 附录（调试 / CI 用）

用户未要求时，Agent 应优先走对话 + Skill，CLI 仅作引擎调用。

```bash
python cursor-novel-writer/engine/novel_cli.py intel scan --period week
python cursor-novel-writer/engine/novel_cli.py init --title "..." --premise "..." --concept ./intel/concepts/xxx.md
python cursor-novel-writer/engine/novel_cli.py pipeline gate --phase 1
python cursor-novel-video/engine/video_cli.py summary --chapter ./novels/<slug>/chapters/01_*.md --subtitles
```

更多触发语：[cursor-novel-writer/skills/novel-pipeline/references/quick-triggers.md](cursor-novel-writer/skills/novel-pipeline/references/quick-triggers.md)
