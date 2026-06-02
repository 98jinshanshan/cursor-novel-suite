# GitHub 发布与上传规范

**版本：** 1.1（2026-06-03）  
**适用范围：** Monorepo `CURSOR/`（含 `cursor-novel-writer` + `cursor-novel-video`）  
**套件版本：** `.novel-suite-root` → `suite-version=2026.06.03-nec`  
**Cursor：** 见 [verification/cursor.md](../verification/cursor.md)（NEC smoke 已跑通）

---

## 1. 发布形态（推荐）

| 方案 | 说明 | 推荐 |
| --- | --- | --- |
| **Monorepo 单仓** | 根目录 `CURSOR`，两子项目同仓 | ✅ 默认 |
| 双仓 | writer / video 各一 repo | 仅当需独立版本号时 |

GitHub 仓库建议名：`cursor-novel-suite` 或 `CURSOR`（与本地一致即可）。

---

## 2. 上传前检查清单

### 2.1 必须忽略（已在 `.gitignore`）

```text
tmp/
**/tmp/video_jobs/
__pycache__/
.venv/
dist/
*.epub
```

### 2.2 必须提交

| 路径 | 说明 |
| --- | --- |
| `cursor-novel-writer/` | Skills + engine + examples/demo-novel |
| `cursor-novel-video/` | Skills + engine + demos/（样片 MP4 若 <5MB 可提交） |
| `docs/` | 审计、规范、路线图 |
| `.github/workflows/ci.yml` | CI |
| `.markdownlint.json` / `.markdownlintignore` | 文档质量 |
| `.cursor/rules/` | Cursor 协作规则（可选公开） |
| `requirements-dev.txt` | 测试依赖 |
| 根 `README.md` | 入口 |

### 2.3 禁止提交

- `.env`、API Key、`credentials.json`
- `cursor-novel-video/tmp/` 下 job 产物
- 用户小说工程 `my-novel/`（若本地创建）
- 体积过大的渲染缓存

### 2.4 本机跑通（Cursor 优先）

在上传前于本机执行：

```powershell
cd G:\CURSOR
pip install -r requirements-dev.txt
pip install -r cursor-novel-writer/requirements.txt
pip install -r cursor-novel-video/requirements.txt

# 文档 0 错误
npx markdownlint-cli2 "cursor-novel-writer/**/*.md" "cursor-novel-video/**/*.md" "docs/**/*.md" "*.md"

# 测试
pytest -m "not ffmpeg" -q

# 小说
cd cursor-novel-writer
py -3 engine/novel_cli.py export --project examples/demo-novel --format epub

# 视频（需 FFmpeg）
cd ..\cursor-novel-video
py -3 engine/video_cli.py summary --chapter ..\cursor-novel-writer\examples\demo-novel\chapters\01_试章.md --subtitles
```

全部通过后，再 `git push`。

---

## 3. GitHub 账号与仓库创建

### 3.1 账号

1. 打开 [https://github.com/signup](https://github.com/signup) 注册（若已有账号跳过）
2. 建议开启 **2FA**
3. （可选）安装 [GitHub CLI](https://cli.github.com/)：`gh auth login`

### 3.2 创建空仓库（Web）

1. GitHub → **New repository**
2. Repository name：`cursor-novel-suite`
3. Description：`Chinese novel Agent Skills + novel-to-video CLI`
4. **Public**（或 Private 按你需要）
5. **不要**勾选 “Add a README” / “Add .gitignore”（本地已有）
6. Create repository

### 3.3 创建空仓库（CLI）

```powershell
gh repo create cursor-novel-suite --public --source=. --remote=origin --push=false
```

---

## 4. 本地 Git 初始化与首次推送

在 `G:\CURSOR` 执行（**首次**）：

```powershell
cd G:\CURSOR

# 若尚未 init
git init
git branch -M main

# 首次添加（确认无 secrets）
git add .
git status   # 人工扫一眼：不应出现 tmp/、*.epub、.env

git commit -m "Initial commit: novel writer + novel video Agent Skills suite"
```

关联远程并推送：

```powershell
# 将 YOUR_USER 换成你的 GitHub 用户名
git remote add origin https://github.com/YOUR_USER/cursor-novel-suite.git
git push -u origin main
```

SSH 方式：

```powershell
git remote add origin git@github.com:YOUR_USER/cursor-novel-suite.git
git push -u origin main
```

---

## 5. GitHub 标准排版（仓库页展示）

### 5.1 README 结构（根目录，已对齐）

1. 项目一句话说明  
2. 文档导航 → `docs/INDEX.md`  
3. 子项目表格  
4. 快速安装（`npx skills add`）  
5. CLI 示例  
6. 质量 / CI  
7. 平台列表  

### 5.2 子项目 README

- `cursor-novel-writer/README.md` — Skills 表、CLI、graphify  
- `cursor-novel-video/README.md` — 管道、MCP、demos  

### 5.3 文档聚合

所有审计/规范/路线图仅在 **`docs/`**，不在 repo 根堆叠 `AUDIT-*.md`。

### 5.4 License

两子项目均为 MIT（`LICENSE` 已存在）。根目录可选增加同名 `LICENSE` 或 README 中链接子项目 License。

### 5.5 CI 徽章（推送后可加至根 README）

```markdown
![CI](https://github.com/YOUR_USER/cursor-novel-suite/actions/workflows/ci.yml/badge.svg)
```

### 5.6 Topics（GitHub 仓库 Settings → Topics）

建议标签：`agent-skills`、`cursor`、`novel`、`epub`、`ffmpeg`、`chinese-fiction`

---

## 6. 推送后验证

| 步骤 | 操作 |
| --- | --- |
| 1 | GitHub → **Actions** 查看 CI 是否绿（lint + pytest） |
| 2 | 克隆到新目录 smoke test：`git clone ... && pytest -m "not ffmpeg"` |
| 3 | Cursor：**Clone Repository** 打开，确认 Skills 路径 |
| 4 | 更新 [docs/verification/cursor.md](../verification/cursor.md) 记录「从 GitHub clone 后」结果 |

---

## 7. 后续：Qoder / TRAE（预留，非本次阻塞）

结构已具备 `platforms/qoder/`、`platforms/trae/` 与 `docs/verification/qoder.md`、`trae-cn.md`。

**未来快速实测模板（clone 同一 GitHub 仓后）：**

```powershell
# Qoder
npx skills add YOUR_USER/cursor-novel-suite/cursor-novel-writer -a qoder -y

# TRAE CN
npx skills add YOUR_USER/cursor-novel-suite/cursor-novel-video -a trae-cn -y
```

结果填入对应 `docs/verification/*.md` 即可，无需改目录结构。

---

## 8. 与 graphify upstream 对照的关系

graphify 真机安装与命令对照见：

- 草案：[cursor-novel-writer/docs/graphify-upstream-commands.md](../../cursor-novel-writer/docs/graphify-upstream-commands.md)
- 实测规程：[cursor-novel-writer/docs/graphify-upstream-verification.md](../../cursor-novel-writer/docs/graphify-upstream-verification.md)

**建议顺序：** Cursor 本机跑通 → GitHub 上传 → 安装 graphify CLI → 填 verification 表。

---

## 9. 常见问题

| 问题 | 处理 |
| --- | --- |
| push 被拒（large file） | 检查是否误提交 MP4/demo；用 `git rm --cached` 移除后重推 |
| CI markdownlint 失败 | 本地运行 `npx markdownlint-cli2 ...` 修完再 push |
| Skills 路径不对 | 必须 clone **完整 monorepo**，见 STRUCTURE-STANDARDS Option A |
| 子目录单独 push | 不推荐；Skills wrapper 依赖 `engine/` |

---

*上传前务必完成 §2.4 本机检查。Qoder/TRAE 实测不阻塞首次 GitHub 发布。*
