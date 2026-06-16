# Trace 与 State 最小模型（F1 规格，无代码）

F1 只定义字段与演进路径，**不**要求立刻重构 `result.py` 或引入 LangGraph。

## 目标

从现有 **JSON Result Contract** 逐步叠加可关联、可审计的运行记录，支撑：

- 长流程恢复（F4 LangGraph PoC 前置）
- 多 IDE 会话对齐
- 商业交付追溯（谁确认 P5、何时 dry-run）

## 最小记录字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `run_id` | string | 一次用户目标的生命周期 ID（如「写完 ch03」） |
| `trace_id` | string | 单次工具调用链 ID（可嵌套 parent_trace_id） |
| `session_id` | string | IDE 会话 / 压缩前归档关联 |
| `agent_surface` | enum | `cursor` / `codex` / `trae-cn` / `qoder` / `openclaw` / `cli` |
| `workflow_id` | string | 如 `novel-pipeline`、`video-chapter-summary` |
| `phase` | string | Phase 0–9 或 video-production 阶段 |
| `step_id` | string | workflow 内步骤（如 `gate_phase5`） |
| `tool_name` | string | CLI 子命令或 MCP tool 名 |
| `permission_level` | string | P0–P5 |
| `input_summary` | string | 脱敏后的输入摘要（无正文全文） |
| `artifact_paths` | string[] | Result.artifacts 路径列表 |
| `result_code` | string | 如 `PRODUCT_VALIDATE_OK` |
| `gate_status` | string | `pass` / `blocked` / `manual_review` |
| `manual_confirmation_required` | bool | P3+ 时为 true |
| `external_call_performed` | bool | P4+ 审计 |
| `next_actions` | string[] | 来自 Result Contract |
| `created_at` | ISO8601 | UTC 时间戳 |

## 与当前 Result Contract 映射

现有 `Result`（`src/novel_suite/core/result.py`）已含：

```text
status, code, message, artifacts, next_actions, required, details
```

**F3 演进（建议）：**

1. **Phase A**：Agent 在调用 CLI 后自行写 `novels/<slug>/.agent-runs/<run_id>.jsonl`，每行追加上述字段 + Result 快照。
2. **Phase B**：CLI 可选 `--run-id` / `--trace-id` 透传进 `details`。
3. **Phase C**：统一 `novel-suite trace append --json` 只写仓内（P2）。
4. **Phase D**：可选 LangGraph checkpointer 对接（F4）。

## 存储边界

- 默认路径：`novels/<slug>/.agent-runs/` 或 `.tmp/agent-traces/`（仓内）
- **禁止** 默认上传 trace 到第三方
- 正文与密钥不得写入 `input_summary`

## Gate 关联

| gate_status | 来源 |
| --- | --- |
| `pass` | `status=ok` 且无 open blockers |
| `blocked` | `GATE_FAIL`、`PRODUCT_VALIDATE_FAIL`、`COMMERCIAL_REVIEW_VALIDATE_FAIL` |
| `manual_review` | C6 `needs_manual_review`、发布前 checklist |

## 示例 JSONL 行（示意）

```json
{
  "run_id": "run_20260601_ch03",
  "trace_id": "tr_8f2a",
  "agent_surface": "cursor",
  "workflow_id": "novel-pipeline",
  "phase": "5",
  "step_id": "chapter_draft",
  "tool_name": "writer.chapter.draft",
  "permission_level": "P2",
  "result_code": "CHAPTER_DRAFT_OK",
  "gate_status": "pass",
  "manual_confirmation_required": false,
  "external_call_performed": false,
  "created_at": "2026-06-01T12:00:00Z"
}
```

## 非目标（F1）

- 不实现 OpenTelemetry exporter
- 不引入 LangGraph Memory
- 不修改 `src/novel_suite` 代码
