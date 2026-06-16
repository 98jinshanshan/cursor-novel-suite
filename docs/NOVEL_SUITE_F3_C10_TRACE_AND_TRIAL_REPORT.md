# Novel Suite 合并报告：F3 Trace/State + C10 多 IDE 试用

**日期：** 2026-06-01  
**任务：** 单会话合并 — Trace/State 最小记录规格 + 多 IDE 试用脚本与反馈回收。

---

## F3 目标

定义可复盘的 **Trace/State 记录语言**（JSON Schema + JSONL 样例 + 映射），衔接 F2 `trace_fields` 与 JSON Result Contract，**不**实现自动采集或
workflow runner。

## C10 目标

提供多 IDE **试用脚本、Trial Cards、反馈 schema/样例、分拣 playbook**，依赖 F3 字段使反馈可比较；**不上传**、**不写**全局 IDE 配置。

---

## 新增/修改文件

### F3（`novel-suite/trace-state/`）

| 类型 | 文件 |
| --- | --- |
| Schema | `trace_state.schema.json`, `trace_event_minimal.schema.json`, `trace_state.schema.md` |
| 模型 | `trace_state_lifecycle.md`, `trace_state_storage_policy.md`, `trace_state_privacy_policy.md`, `trace_state_error_model.md` |
| 映射 | `trace_state_*_mapping.md` × 3, `mappings/*.md` × 3 |
| 样例 | `examples/*.trace.jsonl` × 4 |
| 入口 | `README.md` |

### C10（`novel-suite/multi-ide-trials/`）

| 类型 | 文件 |
| --- | --- |
| 范围/矩阵 | `trial_scope.md`, `trial_matrix.md`, `user_trial_script.md` |
| 反馈 | `trial_feedback_form.schema.json`, `trial_feedback_form.sample.json`, `feedback_triage_playbook.md`, `feedback_summary_template.md` |
| 边界/标准 | `trial_risk_boundary.md`, `trial_success_criteria.md`, `trial_no_external_call_checklist.md`, `ide_surface_notes.md` |
| Trial Cards | `trial_cards/*_trial_card.md` × 6 |
| 入口 | `README.md` |

### 代码（只读校验）

| 文件 | 变更 |
| --- | --- |
| `src/novel_suite/core/trace_state.py` | 新增 F3+C10 validate |
| `src/novel_suite/core/errors.py` | TRACE/MULTI_IDE 错误码 |
| `src/novel_suite/cli.py` | `trace-state validate`, `multi-ide-trials validate` |
| `src/novel_suite/core/product_layer.py` | product validate 覆盖 F3/C10 关键文件 |
| `tests/test_trace_state_specs.py` | 4 tests |
| `tests/test_multi_ide_trials.py` | 5 tests |

### 索引

- `novel-suite/README.md`
- `docs/INDEX.md`
- `NOVEL_SUITE_IMPLEMENTATION_PLAN.md`（F3、C10 ✅）

---

## Trace/State 核心字段

`trace_version`, `run_id`, `trace_id`, `session_id`, `agent_surface`, `ide_name`, `workflow_id`,
`workflow_contract_path`, `phase`, `step_id`, `tool_name`, `permission_level`, `adapter_level`, `input_summary`,
`artifact_paths`, `result_status`, `result_code`, `gate_status`, `commercial_release_allowed`,
`manual_confirmation_required`, `external_call_performed`, `error_summary`, `next_actions`, `created_at`

**默认：** `external_call_performed=false`, `commercial_release_allowed=false`, `adapter_level` A0/A1。

---

## 多 IDE 试用矩阵摘要

| IDE | agent_surface | Trial Card |
| --- | --- | --- |
| Cursor | cursor | `trial_cards/cursor_trial_card.md` |
| Codex | codex | `trial_cards/codex_trial_card.md` |
| TRAE CN | trae-cn | `trial_cards/trae_cn_trial_card.md` |
| Qoder | qoder | `trial_cards/qoder_trial_card.md` |
| OpenClaw | openclaw | `trial_cards/openclaw_trial_card.md` |
| Generic | generic-agent | `trial_cards/generic_agent_trial_card.md` |

五任务：product 列表 → 解释 workflow → `workflow-contract validate` → candidate blocked 检查 → demo feedback。

---

## Feedback schema 字段摘要

`trial_id`, `ide_name`, `agent_surface`, `task_id`, `workflow_id`, `success`, `failure_type`, `confusion_points`,
`missing_context`, `unexpected_behavior`, `trace_sample_path`, `suggested_fix`, `risk_observed`,
`external_call_attempted`（强制 false）。

---

## 继承关系

| 层 | 继承 |
| --- | --- |
| F1 | `permission_level` P0–P5、`agent_surface` |
| F2 | `workflow_id`, `step_id`, `workflow_contract_path`, `trace_fields` |
| C8 | `adapter_level` A0–A5 |
| C9 | `commercial_release_allowed=false`, `gate_status=blocked` 于 release candidate trace |

---

## 测试/验证

| 命令 | 结果 |
| --- | --- |
| `trace-state validate --json` | TRACE_STATE_VALIDATE_OK |
| `multi-ide-trials validate --json` | MULTI_IDE_TRIALS_VALIDATE_OK |
| `product validate` | PRODUCT_VALIDATE_OK |
| `workflow-contract validate` | WORKFLOW_CONTRACT_VALIDATE_OK |
| `commercial-release-candidate validate` | CANDIDATE_GATE_VALIDATE_OK |
| `pytest tests/test_trace_state_specs.py tests/test_multi_ide_trials.py` | 9 passed |

---

## 未执行动作

- 未引入 LangGraph/CrewAI/AutoGen
- 未实现 workflow runner / trace collector 后台
- 未自动采集真实用户行为
- 未上传反馈 / 未写全局 IDE 目录
- 未调用外部服务 / 未执行 adapter
- 未修改 SOLO/Reasonix
- 未将 `commercial_release_allowed` 改为 true

---

## 下一阶段建议

1. **F4**：LangGraph 可选 PoC **设计包**（仅设计）
2. **F5**：RAG/素材库后端候选研究包
3. **C11**：试用反馈复盘与产品包修订
