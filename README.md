# CURSOR — 小说与视频 Agent 工具包

两个独立项目，共享 [Agent Skills 开放标准](https://agentskills.io)。

**文档导航：** [docs/INDEX.md](docs/INDEX.md)（审计报告、目录规范、路线图、[GitHub 发布](docs/standards/GITHUB-RELEASE.md)）

| 项目 | 说明 |
| --- | --- |
| [cursor-novel-writer](./cursor-novel-writer/) | 中文通用小说：立项 → 写作 → graphify 审稿 → EPUB |
| [cursor-novel-video](./cursor-novel-video/) | 章节 → 摘要短视频 / 分场景叙事片 |

## 快速安装（多 IDE）

```bash
npx skills add ./cursor-novel-writer -a cursor -a qoder -a trae-cn -y
npx skills add ./cursor-novel-video -a cursor -a qoder -a trae-cn -y
```

## CLI

```bash
pip install -r cursor-novel-writer/requirements.txt
pip install -r cursor-novel-video/requirements.txt

python cursor-novel-writer/engine/novel_cli.py init \
  --title "书名" --premise "梗概" --output ./my-novel

python cursor-novel-video/engine/video_cli.py summary \
  --chapter ./my-novel/chapters/01_开篇.md
```

## 质量 / CI

```bash
pip install -r requirements-dev.txt
pytest -m "not ffmpeg"    # 默认 smoke（无需 FFmpeg）
pytest -m ffmpeg          # 含视频 E2E
```

GitHub Actions：`.github/workflows/ci.yml`（markdownlint + pytest）

## 平台

Cursor · Qoder · TRAE CN / SOLO · Claude Code · Codex · Copilot 等（见各项目 README）
