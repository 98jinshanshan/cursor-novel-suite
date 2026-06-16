# Solo Demo 15min（P1）

> **首次 O1 / P1 本地只读试用推荐从本目录开始：** 先读本 README → `demo_script_15min.md` → `blocked_boundary.md` → PP-001 首跑指南（`promptpack-first-run/pp001_first_run_guide.md`）→ 只在本地记录反馈。

**个人开发者 15 分钟本地 demo 路线** — 只读 dry-run，**非**商业发布。

```yaml
demo_type: local_readonly_dry_run
external_call_performed: false
commercial_release_allowed: false
verdict: blocked
```

## 目标

15 分钟内理解：产品入口、商业 blocked 边界、PromptPack 新手起点（PP-001）、短剧/视频规格入口、多 IDE dry-run 反馈方式。

## 文件

| 文件 | 用途 |
| --- | --- |
| [demo_script_15min.md](demo_script_15min.md) | 分环节脚本 |
| [demo_checklist.md](demo_checklist.md) | 验收清单 |
| [safe_commands.md](safe_commands.md) | 只读 CLI |
| [blocked_boundary.md](blocked_boundary.md) | 禁止项 |

## 校验

```powershell
novel-suite solo-demo-15min validate --json
```
