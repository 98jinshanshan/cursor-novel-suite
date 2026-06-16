# Novel Suite X1+X2+X3 执行报告

**日期：** 2026-06-01  
**范围：** UI Workbench 运行路线、OpenClaw 复测提示词、ip.to_short_drama 第二 Agent

---

## X1 — 运行路线

| 文件 | 内容 |
| --- | --- |
| `novel-suite/ui-agent-workbench/runbook.md` | 路线 A stdlib + 路线 B 可选 FastAPI |
| `novel-suite/server/runbook.md` | server validate/run + contract-only |

默认不安装 `novel-suite[server]` extra。

## X2 — OpenClaw 复测

| 文件 | 用途 |
| --- | --- |
| `novel-suite/ui-agent-workbench/openclaw_retest_prompt.md` | 可复制给 OpenClaw 的只读复测清单 |

## X3 — ip.to_short_drama

| 组件 | 说明 |
| --- | --- |
| `novel-suite/ip-production-demo/` | 8 artifacts；复用 cold_case_echo_short_drama JSON/CSV |
| `src/novel_suite/core/ip_production_demo.py` | validate + run |
| CLI | `ip-production-demo validate/run --json` |
| API | `POST /api/agents/ip-to-short-drama/run` |
| UI | `btn-ip-drama` 可点击 |
| Menu | `ip.to_short_drama` → `demo-runnable` |

## 验证（2026-06-01）

| 命令 | 结果 |
| --- | --- |
| agent-entry-menu validate | OK |
| ip-production-demo validate | OK |
| server validate | OK |
| product validate | OK |
| commercial-release-candidate validate | OK，`verdict=blocked` |
| 专项 pytest | 20 passed |

## 边界

- `commercial_release_allowed=false` 未改
- `novel.create` 仍 planned/disabled
- 未联网；未执行真实视频/adapter
