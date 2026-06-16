# Novel Suite 合并报告：C8+C9 只读复核 + F2 Workflow Contract

**日期：** 2026-06-01  
**任务：** 单会话合并 — 不重做 C8/C9，执行 F2 工作流契约包。

---

## A. C8+C9 只读复核

### 文件存在性

| 路径 | 状态 |
| --- | --- |
| `video-production/adapter-security-review/README.md` | ✅ 已复核 |
| `adapter-security-review/adapter-readiness-matrix.md` | ✅ 已复核 |
| `commercial-release-candidate/README.md` | ✅ 已复核 |
| `commercial-release-candidate/final-release-gate.md` | ✅ 已复核 |
| `docs/NOVEL_SUITE_C8C9_SECURITY_AND_RELEASE_GATE_REPORT.md` | ✅ 已复核 |
| `tests/test_adapter_security_review.py` | ✅ 已复核 |
| `tests/test_commercial_release_candidate.py` | ✅ 已复核 |

### 状态确认

| 项 | 复核结果 |
| --- | --- |
| `commercial_release_allowed` | **false**（final-release-gate + candidate manifest + validate 输出） |
| `verdict` | **blocked** |
| B01–B04 | **open**（known-blockers.md、release-blockers.md） |
| B05 | **resolved-demo-only** / `B05-resolved-demo-manifest-fields-only` |
| 真实 adapter 执行 | **仍禁止**（readiness matrix `blocked_until_C8_review_and_user_confirmation`） |
| 默认外部调用 | **未开启**（C5 dry-run only，无 A2+ 代码） |

### 复核 CLI（本机）

- `commercial-review validate` → `COMMERCIAL_REVIEW_VALIDATE_OK`
- `commercial-release-candidate validate` → `CANDIDATE_GATE_VALIDATE_OK`

**结论：** C8/C9 产物完整，与用户提供汇总一致；**未重做** C8/C9。

---

## B. F2 执行结果

### 目标

将分散工作流抽象为 **Workflow Contract** JSON Schema + 7 样例 + 映射文档；**非** LangGraph 运行时。

### 新增/修改文件

**F2 文档（`novel-suite/workflow-contracts/`）**

- Schema：`workflow_contract.schema.json`、`workflow_contract_minimal.schema.json`
- 说明：`workflow_contract.schema.md`、lifecycle/gate/permission/artifact/human_review/error 模型
- 样例：`examples/*.contract.json` × 7
- 映射：`mappings/*.md` × 4

### 代码（只读校验）

| 文件 | 变更 |
| --- | --- |
| `src/novel_suite/core/workflow_contracts.py` | 新增 |
| `src/novel_suite/core/product_layer.py` | `workflow_contracts` category + validate |
| `src/novel_suite/cli.py` | `workflow-contract validate` |
| `src/novel_suite/core/errors.py` | F2 错误码 |
| `tests/test_workflow_contracts.py` | 7 tests |

### 索引

- `novel-suite/README.md`、`docs/INDEX.md`、`NOVEL_SUITE_IMPLEMENTATION_PLAN.md`（F2 ✅）

### 核心字段

`workflow_id`、`workflow_type`、`permission_level`（P0–P5）、`steps`、`gates`、`artifacts`、`external_calls`、`commercial_boundary`、`trace_fields`、`next_actions`。

### 7 个 sample 映射

| Contract | 来源 |
| --- | --- |
| `chapter_writing` | `core/workflows/chapter_writing.md` |
| `chapter_review` | `core/workflows/chapter_review.md` |
| `novel_to_video` | `core/workflows/novel_to_video.md` |
| `novel_to_short_drama` | `video-production/workflows/novel_to_short_drama.md` |
| `adapter_dry_run` | C5 + C8（A1/P1） |
| `commercial_preflight` | C6/C7 |
| `commercial_release_candidate` | C8/C9 |

### C8/C9 → `commercial_release_candidate.contract.json`

```json
"commercial_boundary": {
  "commercial_release_allowed": false,
  "verdict": "blocked",
  "blockers": { "B01":"open", "B02":"open", "B03":"open", "B04":"open", "B05":"resolved-demo-only" }
}
```

### 仍为 blocked / demo_only

- 全部 7 contract：`external_calls.allowed=false`
- 全部：`commercial_release_allowed=false`
- release candidate：`verdict=blocked`
- preflight：`demo_only`

### 测试/验证

| 命令 | 结果 |
| --- | --- |
| `workflow-contract validate --json` | WORKFLOW_CONTRACT_VALIDATE_OK |
| `product validate` | PRODUCT_VALIDATE_OK |
| `pytest tests/test_workflow_contracts.py -q` | 7 passed |
| 合并相关套件 | 34 passed |
| `pytest -m "not ffmpeg"` | **459 passed**, 2 skipped |

---

## 未执行动作

- 未重做 C8/C9
- 未引入 LangGraph/CrewAI/AutoGen 等依赖
- 未实现 workflow runner / graph executor
- 未调用外部服务 / 未执行 adapter
- 未修改 SOLO/Reasonix
- 未将 `commercial_release_allowed` 改为 true
- 未发布/上传/外发

---

## 下一阶段建议

1. **F3：** Trace/State 最小记录规格包（衔接 `trace_fields`）
2. **C10：** 多 IDE 用户试用脚本与反馈回收包
3. **F4：** LangGraph 可选 PoC 设计包（仅设计）
