# Novel Suite Q1/Q2/Q3 反馈承接与 Backlog 归类报告

**日期：** 2026-06-13  
**任务：** 建立真实试跑反馈承接机制 — **非**伪造反馈、**非**自动改 PromptPack、**非**自动应用 backlog。

---

## 目标与边界

| 阶段 | 目标 | 禁止 |
| --- | --- | --- |
| Q1 | 本地 demo 真实试跑记录承接 | Agent 代填体验结论 |
| Q2 | PromptPack 首跑卡点 → 修订候选 | 自动改 PP-001/002/003 |
| Q3 | 多 IDE 反馈 backlog 归类 | 自动应用 backlog / 遥测 |

全程保持：`commercial_release_allowed=false`、`verdict=blocked`。

---

## 新增目录

### Q1 — `novel-suite/solo-demo-trial-intake/`

- `README.md`、`trial_record_template.md`、`trial_result_summary_template.md`
- `no_fake_trial_policy.md`
- `solo-demo-trial-intake.schema.json`、`solo-demo-trial-intake.sample.json`

### Q2 — `novel-suite/promptpack-friction-review/`

- `README.md`、`friction_record_template.md`、`revision_candidate_template.md`
- `no_auto_promptpack_change_policy.md`
- `promptpack-friction-review.schema.json`、`promptpack-friction-review.sample.json`

### Q3 — `novel-suite/multi-ide-feedback-backlog/`

- `README.md`、`backlog_taxonomy.md`、`backlog_item_template.md`
- `triage_rules.md`、`no_auto_backlog_apply_policy.md`
- `multi-ide-feedback-backlog.schema.json`、`multi-ide-feedback-backlog.sample.json`

### 本地待填 — `.tmp/novel-suite-q/`

| 子目录 | 用途 |
| --- | --- |
| `solo-demo-trial-intake/` | Q1 用户试跑记录 |
| `promptpack-friction-review/` | Q2 卡点与修订候选 |
| `multi-ide-feedback-backlog/` | Q3 backlog 项 |

各含 `README.md` + `.gitkeep`；**无**预填真实反馈。

---

## 工程接入

```powershell
novel-suite solo-demo-trial-intake validate --json
novel-suite promptpack-friction-review validate --json
novel-suite multi-ide-feedback-backlog validate --json
```

代码：`delivery_readiness.py`、`product_layer.py`、`cli.py`、`errors.py`  
测试：`tests/test_q_feedback_intake_and_backlog.py`

---

## 商业发布

**仍 blocked** — 不伪造反馈、不自动修订、不关闭 B01–B04。

---

## 下一阶段建议

- **R1：** 用户真实填写 Q1/Q2/Q3 后的只读承接
- **R2：** 高优先级卡点修订方案
- **R3：** 是否进入小版本 demo 迭代候选
