# Novel Suite 合并报告：G1 交付索引 + G2 演示路线 + G3 法律复核

**日期：** 2026-06-01  
**任务：** 交付整理层 — **非**商业发布。

---

## G1 交付总索引结论

- 新增 `novel-suite/delivery-hub/`：start-here、四类角色入口、能力地图、安全演示路径、blockers 摘要
- 用户入口：`delivery-hub/start-here.md` → validate 链 → 按角色分流
- 明确包含/不包含；B01–B04 open，B05 resolved-demo-only
- CLI：`novel-suite delivery-hub validate`

## G2 演示路线结论

- 新增 `novel-suite/demo-roadmap/`：15min/45min 脚本、人工试用计划、失败 playbook、claims 边界
- 仅展示 read-only validate + 文档；不展示成片/发布/API
- 禁止话术：收益保证、版权保证、已可发布
- CLI：`novel-suite demo-roadmap validate`

## G3 法律复核结论

- 新增 `novel-suite/legal-release-review/`：B01–B05 关闭条件、第三方/许可/权利/claims 清单、签字模板
- `legal_conclusion_auto_generated=false`；只定义解除条件，**不**解除门禁
- 维持：`commercial_release_allowed=false`、`verdict=blocked`
- CLI：`novel-suite legal-release-review validate`

---

## 仍然 blocked 的原因

| 项 | 状态 |
| --- | --- |
| B01 法律复核 | open |
| B02 commercial gate | open |
| B03 成片权利/质量 | open |
| B04 adapter A2+ | open |
| B05 manifest | resolved-demo-only，权利人工待确认 |
| verdict | **blocked** |

G 阶段是**准备交付与演示**，不是批准销售或发布。

---

## 新增/修改文件

### G1 `delivery-hub/`（14 文件）

README、start-here、delivery-map、capability-index、safe-demo-path、cold-start-checklist、role-based-onboarding、ide-entrypoints、what-is-included/not-included、known-blockers-summary、glossary、schema、sample

### G2 `demo-roadmap/`（15 文件）

README、scope、storyline、15/45min
脚本、checklist、manual_trial_plan、artifact_list、success/failure、claims_boundary、no_external_call、feedback_capture、schema、sample

### G3 `legal-release-review/`（14 文件）

README、scope、6 类 checklist、adapter/platform review、decision record、signatures、blocker_closure_policy、schema、sample

### 代码

- `src/novel_suite/core/delivery_readiness.py`
- `cli.py` — 三个 validate 子命令
- `product_layer.py` — 关键文件检查
- `tests/test_delivery_hub.py`（5 tests）
- `tests/test_demo_and_legal_review.py`（7 tests）

### 索引

- `novel-suite/README.md`, `docs/INDEX.md`, `NOVEL_SUITE_IMPLEMENTATION_PLAN.md`（G 阶段表）

---

## 验证结果

| 命令 | 结果 |
| --- | --- |
| `delivery-hub validate` | DELIVERY_HUB_VALIDATE_OK |
| `demo-roadmap validate` | DEMO_ROADMAP_VALIDATE_OK |
| `legal-release-review validate` | LEGAL_RELEASE_REVIEW_VALIDATE_OK |
| `product validate` | PRODUCT_VALIDATE_OK |
| `commercial-release-candidate validate` | OK |
| `future-backends validate` | OK |
| `trial-feedback-review validate` | OK |
| 专项 pytest | 12 passed |

---

## 未执行动作

- 未改 `commercial_release_allowed=false`
- 未给出法律结论 / 未代律师签字
- 未发布/上传/外发
- 未调用外部服务 / 未执行 adapter
- 未修改 SOLO/Reasonix
- 未安装 LangGraph/RAG 依赖

---

## 下一阶段建议

1. **H1**：人工试用执行与反馈填报（按 G2/C10）
2. **H2**：产品包冻结候选与版本命名（B8 预备）
3. **H3**：法律复核材料交给人工/律师（G3 清单执行）
