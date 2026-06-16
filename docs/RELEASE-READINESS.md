# Release Readiness（Novel Suite 2.0）

**版本：** 1.0（2026-06-03）  
**范围：** `novel-suite` CLI（writer A–I + video G），legacy `novel_cli.py` / `video_cli.py` 保持兼容。

---

## 验收状态（已复核）

| 模块 | 能力 | 验证 |
| --- | --- | --- |
| Writer | `doctor` / `scan` / `init` / `gate` / `chapter draft` / `export` + `--json` | pytest + 人工 JSON |
| Video | `create-summary` / `run` / `status` / `resume` + `--json` | 非 FFmpeg + FFmpeg |
| 质量门 | `platforms/final-verify.ps1` | CI 对齐 markdownlint + pyright + pytest |

**主链路：**

```text
Writer: doctor → scan → init → gate → chapter draft → export
Video:  create-summary → run / status / resume  (或 create-summary --run)
```

OpenClaw
冒烟清单：[skills/openclaw-novel-suite/references/smoke-checklist.md](../skills/openclaw-novel-suite/references/smoke-checklist.md)

---

## 发布前一键检查

```powershell
cd G:\CURSOR
$env:NOVEL_SUITE_ROOT = 'G:\CURSOR'
pip install -e .
powershell -File platforms/final-verify.ps1
py -3 -m pytest cursor-novel-video/tests -m ffmpeg -q
```

期望：`final-verify` → `OK: all checks passed`；ffmpeg → `1 passed`。

---

## 端到端示例（可复制）

环境：`NOVEL_SUITE_ROOT` 指向 Monorepo 根（含 `.novel-suite-root`）。

### 1. Writer — 新书链路（demo / 离线）

```powershell
novel-suite doctor --core-only --json
novel-suite writer scan --demo --period week --json
# 从 details.themes / intel/concepts 选一概念路径 CONCEPT

novel-suite writer init --title "验收书" --premise "梗概一句。" `
  --concept intel/concepts/<file>.md --json
# 记下 details.slug，例如 novels/<slug>

novel-suite writer gate --phase 1 --project novels/<slug> --json
```

### 2. Writer — 导出（demo-novel，无需新建书）

```powershell
novel-suite writer export `
  --project cursor-novel-writer/examples/demo-novel `
  --format markdown --json
# code: EXPORT_OK；artifacts 含 dist/*.md
```

### 3. Video — 分步 job（推荐 Agent）

```powershell
novel-suite video create-summary `
  --chapter 01_试章.md `
  --project cursor-novel-writer/examples/demo-novel --json
# VIDEO_CREATE_OK, details.job_id, status=pending

novel-suite video run --job <job_id> --json
novel-suite video status --job <job_id> --json
# 成功: VIDEO_RUN_OK / VIDEO_STATUS_OK, status=succeeded, artifacts 含 *.mp4
```

### 4. Video — 一步跑（需 FFmpeg）

```powershell
novel-suite video create-summary `
  --chapter 01_试章.md `
  --project cursor-novel-writer/examples/demo-novel `
  --run --json
# PowerShell: (... --json) | ConvertFrom-Json  → code VIDEO_RUN_OK
```

---

## 本地清理测试生成物

以下目录默认 **gitignore**，但会污染本地 registry / 磁盘：

| 路径 | 说明 |
| --- | --- |
| `novels/<slug>/`（非 README） | init / pytest 冒烟书目 |
| `novels/_registry.json` / `novels/.active` | 登记与活动书 |
| `cursor-novel-video/tmp/video_jobs/*` | 视频 job 工件 |

**重置脚本（PowerShell）：**

```powershell
cd G:\CURSOR
Get-ChildItem novels -Directory | Remove-Item -Recurse -Force
Remove-Item novels\.active -Force -ErrorAction SilentlyContinue
[System.IO.File]::WriteAllText(
  "$PWD\novels\_registry.json",
  '{"version":1,"novels":[],"active_slug":null}',
  [System.Text.UTF8Encoding]::new($false)
)
Get-ChildItem cursor-novel-video\tmp\video_jobs -Directory -ErrorAction SilentlyContinue |
  Remove-Item -Recurse -Force
```

保留：`cursor-novel-writer/examples/demo-novel/`（示例工程，不进 `novels/` registry）。

---

## 已知非阻塞项

- pyright：`video_node_completion.py` 对 `scripts.node_completion` 的 import warning（既有）
- `novels/`、`intel/radar/*.md` 用户数据 gitignore；CI 用 `test_intel_radar_markdown.py` 契约

---

## 相关文档

- [RELEASE-NOTES-2.0.md](./RELEASE-NOTES-2.0.md) — 版本说明（冻结功能范围）
- [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)
- [standards/FINAL-VERIFICATION.md](./standards/FINAL-VERIFICATION.md)
- [plans/ROADMAP.md](./plans/ROADMAP.md)
- [verification/NEC-smoke-matrix.md](./verification/NEC-smoke-matrix.md)
