# CURSOR — 小说与视频 Agent 工具包

两个独立项目，共享 [Agent Skills 开放标准](https://agentskills.io)。

**GitHub：** <https://github.com/98jinshanshan/cursor-novel-suite>  
**SOLO/TRAE：** [solo-clone-checklist.md](docs/verification/solo-clone-checklist.md)  
**SOLO 同步：** `platforms/solo-sync.ps1` · **Phase 0：** [SKILLS-INSTALL.md](docs/standards/SKILLS-INSTALL.md)

**文档导航：** [docs/INDEX.md](docs/INDEX.md) · **[Agent 对话入口（主路径）](AGENTS.md)**  
**目录架构 2.0：** [DIRECTORY-ARCHITECTURE.md](docs/standards/DIRECTORY-ARCHITECTURE.md) ·  
可选 [novel-suite.code-workspace](novel-suite.code-workspace) 打开

| 项目 | 说明 |
| --- | --- |
| [cursor-novel-writer](./cursor-novel-writer/) | 中文通用小说：**novel-pipeline 全流程** → graphify 审稿 → EPUB |
| [cursor-novel-video](./cursor-novel-video/) | 章节 → 摘要短视频 / 分场景叙事片 |

---

## 怎么用（Agent 对话 — 推荐）

1. 用 IDE 打开 **Novel Suite 根目录**（含 `.novel-suite-root`，路径任意）
2. 安装 Skills 并自检（一次性）：

```bash
npx skills add ./cursor-novel-writer -a cursor -a qoder -a trae-cn -y
npx skills add ./cursor-novel-video -a cursor -a qoder -a trae-cn -y
py -3 cursor-novel-writer/engine/novel_cli.py suite doctor
```

Windows：`powershell -File platforms/install-skills.ps1 -Agents cursor`

**GitHub 更新：** `git pull` 后 `powershell -File platforms/patch-update.ps1 -Agents cursor`

3. 打开 **Agent 对话窗口**，直接说（示例）：

```text
按 novel-pipeline 执行 Phase 0：全平台扫榜选题，生成 radar 和 concept 候选，等我确认。
```

```text
我确认 concept 后，请 init 新书并 pipeline gate --phase 1，然后写第一章。
```

```text
把 active 小说最新章节做成 9:16 摘要短视频并加字幕。
```

完整话术与各 IDE 差异见 **[AGENTS.md](AGENTS.md)**。

---

## 各 IDE 快速对照

| IDE | 打开工作区 | Skills 安装位置 | 对话入口 |
| --- | --- | --- | --- |
| Cursor | Novel Suite 根 | `.cursor/skills/`（`install-skills.ps1 -Agents cursor`） | Agent 模式 + [AGENTS.md](AGENTS.md) |
| Qoder | Novel Suite 根 | `.qoder/skills/` | Agent 对话 |
| TRAE / SOLO | Novel Suite 根 | `.trae/skills/` | Agent 对话 / `#novel-pipeline` |

验证与排障：[docs/verification/](docs/verification/)

---

## CLI 附录（引擎 / 调试 / CI）

Agent 会在后台调用；你也可以手动执行：

```bash
pip install -r cursor-novel-writer/requirements.txt
pip install -r cursor-novel-video/requirements.txt

python cursor-novel-writer/engine/novel_cli.py suite doctor
python cursor-novel-writer/engine/novel_cli.py intel scan --period week
python cursor-novel-writer/engine/novel_cli.py init \
  --title "书名" --premise "梗概" --concept ./intel/concepts/<topic>.md
python cursor-novel-writer/engine/novel_cli.py pipeline gate --phase 1
python cursor-novel-video/engine/video_cli.py summary \
  --chapter ./novels/<slug>/chapters/01_开篇.md --subtitles
```

## 质量 / CI

```bash
pip install -r requirements-dev.txt
pytest -m "not ffmpeg"
powershell -File .\typecheck.ps1 -SkipInstall -ChangedOnly
py -3 cursor-novel-writer/engine/novel_cli.py suite doctor --core-only
```

GitHub Actions：`.github/workflows/ci.yml`（markdownlint + pyright + pytest）

## 平台

Cursor · Qoder · TRAE CN / SOLO · Claude Code · Codex · Copilot
