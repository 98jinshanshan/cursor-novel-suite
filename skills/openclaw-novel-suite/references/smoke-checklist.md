# OpenClaw Smoke Checklist（发布前）

在对外宣称「Novel Suite 可用」前，按序执行。全部 `--json`；stdout 必须能 `json.loads`（PowerShell：`ConvertFrom-Json`）。

## 环境

```powershell
cd <NOVEL_SUITE_ROOT>
$env:NOVEL_SUITE_ROOT = '<NOVEL_SUITE_ROOT>'
pip install -e .
```

---

## A. 自动化（必须先过）

| # | 命令 | 期望 |
| --- | --- | --- |
| A1 | `powershell -File platforms/final-verify.ps1` | `OK: all checks passed` |
| A2 | `py -3 -m pytest -m "not ffmpeg" -q` | 全绿（约 99+ passed） |
| A3 | `py -3 -m pytest cursor-novel-video/tests -m ffmpeg -q` | `1 passed`（需 FFmpeg） |

---

## B. Writer JSON 冒烟

| # | 命令 | 期望 `code` |
| --- | --- | --- |
| B1 | `novel-suite doctor --core-only --json` | `DOCTOR_OK` 或等价 ok |
| B2 | `novel-suite writer scan --demo --json` | `SCAN_OK` |
| B3 | `novel-suite writer init --title T --premise P --slug smoke-openclaw --json` | `INIT_OK` |
| B4 | `novel-suite writer gate --phase 1 --project novels/smoke-openclaw --json` | `GATE_OK` |
| B5 | `novel-suite writer export --project cursor-novel-writer/examples/demo-novel --format markdown --json` | `EXPORT_OK` |

B3 后可选清理：`novels/smoke-openclaw`（见 [RELEASE-READINESS.md](../../../docs/RELEASE-READINESS.md)）。

---

## C. Video JSON 冒烟（demo 章）

| # | 命令 | 期望 `code` |
| --- | --- | --- |
| C1 | `novel-suite video create-summary --chapter 01_试章.md --project cursor-novel-writer/examples/demo-novel --json` | `VIDEO_CREATE_OK`，`details.status=pending` |
| C2 | `novel-suite video run --job <job_id> --json` | `VIDEO_RUN_OK`，artifacts 含 `.mp4` |
| C3 | `novel-suite video status --job <job_id> --json` | `VIDEO_STATUS_OK`，`details.status=succeeded` |
| C4 | `novel-suite video create-summary ... --run --json` | `VIDEO_RUN_OK` |

失败时：报告 `message`、`next_actions`；`VIDEO_RUN_FAILED` 时附 `details.reason` / `legacy_output`。

---

## D. 禁止项（Agent）

- 不要用「截取首个 `{`」解析 stdout
- 不要在 gate `error` 时继续写章 / 导出 / 跑视频
- 不要 `writer init --json` 后忽略 `details.legacy_output` 以外的 stderr 当成功

---

## E. 签收

- [ ] A1–A3 通过
- [ ] B1–B5 通过（或 B3 跳过并说明无写权限）
- [ ] C1–C3 通过；C4 在具备 FFmpeg 时通过
- [ ] 本地测试书目 / 旧 `video_jobs` 已按 RELEASE-READINESS 清理（可选）
