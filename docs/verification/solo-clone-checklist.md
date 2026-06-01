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

## 补丁式更新（已克隆 SOLO 项目）

在 **Novel Suite 根目录** 一键执行：

```powershell
powershell -File platforms/patch-update.ps1 -Agents trae-cn
```

等价于：`git pull` → 重装 Skills junction → pip → `suite doctor` → Phase 0 文件检查 → pytest（31 passed）。

**无 git 时：** 重新下载最新 zip 覆盖代码（保留 `novels/`、`intel/concepts/` 用户数据），再运行：

```powershell
powershell -File platforms/install-skills.ps1 -Agents trae-cn
py -3 cursor-novel-writer/engine/novel_cli.py suite doctor
```

**最低版本：** 含 commit `5f1a23e`（`novel_bind` 修复 + 本文档）。

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

## 自动化测试（可选）

```powershell
py -3 -m pytest cursor-novel-writer/tests cursor-novel-video/tests -m "not ffmpeg" -q
```

**通过标准：** **31 passed**（2026-06 起）。

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
│   └── patch-update.ps1     ← 补丁更新
└── AGENTS.md
```
