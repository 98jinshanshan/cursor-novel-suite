# SOLO / TRAE 克隆后安装清单

**适用：** 从 GitHub 下载 zip / clone 到新目录（如 `g:\SOLO小说项目\cursor-novel-suite`）  
**仓库：** <https://github.com/98jinshanshan/cursor-novel-suite>

---

## 常见错误（SOLO 实测）

| 错误做法 | 后果 |
| --- | --- |
| IDE 只打开 `cursor-novel-writer/` 子目录 | Option A 脚本找不到 `engine/scripts/` |
| 只下载 13 个 `SKILL.md` | wrapper 脚本缺失，intel scan / export 失败 |
| 只上传 SOLO Agent、不跑 `install-skills.ps1` | 对话可见 Agent 但「找不到 skill」 |
| 在错误目录跑 `suite doctor` | 报 suite_root FAIL |

**正确：** IDE 工作区 = **含 `.novel-suite-root` 的 monorepo 根**（与 `cursor-novel-writer/`、`cursor-novel-video/` 同级）。

---

## 标准安装（Windows）

```powershell
# 1. 克隆（任选目录）
git clone https://github.com/98jinshanshan/cursor-novel-suite.git
cd cursor-novel-suite

# 2. 用 TRAE/SOLO 打开上述目录（不是子文件夹）

# 3. 依赖
pip install -r requirements-dev.txt
pip install -r cursor-novel-writer/requirements.txt
pip install -r cursor-novel-video/requirements.txt

# 4. Skills（TRAE CN）
powershell -File platforms/install-skills.ps1 -Agents trae-cn

# 5. 自检
py -3 cursor-novel-writer/engine/novel_cli.py suite doctor --core-only
py -3 cursor-novel-writer/engine/novel_cli.py suite doctor
```

zip 下载时：解压后进入**含 `.novel-suite-root` 的那一层**再打开 IDE。

---

## 全流程 smoke（Agent 对话）

| 步骤 | 输入 | 预期 |
| --- | --- | --- |
| 0 | `请运行 novel suite doctor` | 核心项 OK；`.trae/skills` 13 个 |
| 1 | `#novel-market-scan 执行本周 intel scan` | `intel/radar/*.md` |
| 2 | `#novel-pipeline 显示 pipeline status` | Phase 列表 |
| 3 | `把 demo 第1章做成 9:16 summary 视频` | `tmp/video_jobs/.../output/*.mp4` |

SOLO System Prompt 模板：[solo-agent-prompt.md](../../cursor-novel-writer/platforms/trae/solo-agent-prompt.md)

---

## 自动化测试（可选）

```powershell
py -3 -m pytest cursor-novel-writer/tests cursor-novel-video/tests -m "not ffmpeg" -q
```

**通过标准：** writer + video 全部 passed（2026-06 起应为 **31 passed**）。  
若 video 报 `cannot import suite_paths` → 更新到最新 `main`（X-08 已修复 `novel_bind.py`）。

---

## 目录结构速查

```text
cursor-novel-suite/          ← IDE 打开这一层
├── .novel-suite-root
├── .trae/skills/            ← install-skills.ps1 生成（勿手抄 SKILL.md）
├── cursor-novel-writer/skills/   ← 源 Skills
├── cursor-novel-video/skills/
├── platforms/install-skills.ps1
└── AGENTS.md
```
