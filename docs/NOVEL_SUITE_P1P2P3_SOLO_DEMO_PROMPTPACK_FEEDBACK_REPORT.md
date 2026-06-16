# Novel Suite P1/P2/P3 本地 Demo 与 PromptPack 体验优化报告

**日期：** 2026-06-13  
**任务：** P1 15 分钟 demo + P2 PromptPack 首跑 + P3 多 IDE 反馈模板 — **非**商业发布。

---

## 目标与边界

| 阶段 | 目标 | 边界 |
| --- | --- | --- |
| P1 | 压缩 15 分钟只读 demo 路线 | 仅 validate/list/read；无 adapter |
| P2 | PP-001 新手起点与三 Pack 首跑指南 | 无商业宣称；虚构短例 |
| P3 | 统一 6 IDE dry-run 反馈格式 | 本地收集；无遥测 |

全程保持：`commercial_release_allowed=false`、`verdict=blocked`。

---

## 新增目录

### P1 — `novel-suite/solo-demo-15min/`

- `README.md`、`demo_script_15min.md`、`demo_checklist.md`
- `safe_commands.md`、`blocked_boundary.md`
- `solo-demo-15min.schema.json`、`solo-demo-15min.sample.json`

### P2 — `novel-suite/promptpack-first-run/`

- `README.md`、`pp001_first_run_guide.md`、`pp002_review_first_run_guide.md`、`pp003_video_first_run_guide.md`
- `input_output_examples.md`、`common_confusions.md`
- `promptpack-first-run.schema.json`、`promptpack-first-run.sample.json`

### P3 — `novel-suite/multi-ide-dry-run-feedback/`

- `README.md`、`feedback_template.md`、`ide_matrix.md`
- `local_collection_policy.md`、`no_telemetry_policy.md`
- `multi-ide-dry-run-feedback.schema.json`、`multi-ide-dry-run-feedback.sample.json`

---

## 工程接入

```powershell
novel-suite solo-demo-15min validate --json
novel-suite promptpack-first-run validate --json
novel-suite multi-ide-dry-run-feedback validate --json
```

代码：`delivery_readiness.py`、`product_layer.py`、`cli.py`、`errors.py`  
测试：`tests/test_solo_demo_promptpack_feedback.py`

---

## 商业发布

**仍 blocked** — 本阶段不创建 tag/zip/release，不关闭 B01–B04，不调用外部服务。

---

## 下一阶段建议

- **Q1：** 本地 demo 实际试跑记录承接
- **Q2：** PromptPack 真实首跑卡点修订
- **Q3：** 多 IDE 反馈汇总与 backlog 归类
