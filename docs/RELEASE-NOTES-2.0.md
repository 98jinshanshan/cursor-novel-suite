# Release Notes — Novel Suite 2.0.0

**状态：** 功能冻结（2026-06-03）  
**包版本：** `novel-suite==2.0.0`（`pyproject.toml`）  
**签收：** [RELEASE-READINESS.md](./RELEASE-READINESS.md) ·
[smoke-checklist.md](../skills/openclaw-novel-suite/references/smoke-checklist.md)

---

## 概要

统一 CLI `novel-suite`，为 OpenClaw / Agent 提供 **JSON Result Contract**（`--json` 整段 stdout 可 `json.loads`）。  
Legacy `novel_cli.py` / `video_cli.py` 保持可用，不破坏 Cursor / Qoder / TRAE 现有路径。

---

## Writer（`novel-suite writer *`）

| 能力 | 命令要点 | 结果码示例 |
| --- | --- | --- |
| 健康检查 | `doctor --json` | `DOCTOR_OK` |
| 扫榜 / 雷达 | `scan --demo --json` | `SCAN_OK` |
| 立项 | `init --concept … --json` | `INIT_OK`（legacy 进 `details.legacy_output`） |
| 阶段门控 | `gate --phase N --json` | `GATE_OK` / 结构化 `GATE_FAIL` |
| 写章 | `chapter draft --json` | Phase 5 gate；`--skip-gate` 需 env |
| 导出 | `export --format markdown\|txt\|epub --json` | Phase 9 gate；`EXPORT_OK` |

**主链路：** `doctor → scan → init → gate → chapter draft → export`

---

## Video（`novel-suite video *`）

| 能力 | 说明 |
| --- | --- |
| `create-summary` | 建 job，`pending` / `intake` |
| `run` / `status` / `resume` | 状态机；stdout 纯 JSON |
| `create-summary --run` | 一步建+跑（需 FFmpeg） |

Legacy：`video_cli.py summary|drama` 未改。

---

## 工程与质量

- 包布局：`src/novel_suite/` + `pip install -e .`
- 测试：`pytest -m "not ffmpeg"`（99+）；`pytest -m ffmpeg`（视频管线）
- 本地验收：`platforms/final-verify.ps1`（pytest + pyright + markdownlint + intel 雷达契约）
- OpenClaw：`skills/openclaw-novel-suite/`
- Registry：`_registry.json` 使用 `utf-8-sig` 读取（兼容 Windows BOM）

---

## 已知限制（非阻塞）

- pyright：`video_node_completion` import warning（既有）
- `novels/`、`intel/radar/*.md`、`tmp/video_jobs/` 为本地/gitignore 用户数据
- 发版前需按 [RELEASE-READINESS.md](./RELEASE-READINESS.md) 清理测试生成物

---

## 升级说明

1. `pip install -e .` 于 Monorepo 根目录  
2. 设置 `NOVEL_SUITE_ROOT` 或在工作区根打开项目  
3. Agent 调用统一加 `--json`；勿解析「首个 `{`」  
4. 视频分步：`create-summary` → `run` → `status`（或 `--run`）

---

## 发布步骤（需要时）

见 [standards/GITHUB-RELEASE.md](./standards/GITHUB-RELEASE.md)。

人工冒烟： [smoke-checklist.md](../skills/openclaw-novel-suite/references/smoke-checklist.md)。
