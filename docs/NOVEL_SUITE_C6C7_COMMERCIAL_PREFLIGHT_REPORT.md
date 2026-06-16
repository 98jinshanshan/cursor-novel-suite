# Novel Suite 阶段 C6+C7 执行报告 — 商业前置与销售页/交付包审查

**日期：** 2026-06-01  
**范围：** 文档、审查清单、只读校验；不调用外部服务、不启用真实 adapter。

---

## 目标

将 C1–C5 工程能力转化为可审计的商业发布前框架：样例包权利/质量/adapter 审查（C6）、销售页 claims 与交付包门禁（C7）。

---

## 新增/修改文件

### C6 — `novel-suite/video-production/commercial-review/`（10 文件）

| 文件 | 说明 |
| --- | --- |
| `README.md` | 目录索引与 verdict 规则 |
| `sample-package-review.md` | 样例包范围（`demo_only`） |
| `asset-rights-review.md` | 资产七字段权利审查 |
| `prompt-and-copy-originality-review.md` | 原创性审查 |
| `adapter-risk-review.md` | dry-run adapter 风险 |
| `quality-gate-review.md` | scorecard/taxonomy/repair 引用 |
| `manual-review-checklist.md` | 人工复核清单 |
| `release-blockers.md` | P0/P1 阻断项 |
| `sample-package-manifest.schema.json` | manifest 契约 |
| `sample-package-manifest.sample.json` | C6 合规 manifest 样例 |

### C7 — `novel-suite/commercialization/`（11 文件）

| 文件 | 说明 |
| --- | --- |
| `README.md` | 目录索引 |
| `sales-page-preflight.md` | 销售页自检 |
| `claims-allowed.md` / `claims-forbidden.md` | 允许/禁止承诺 |
| `delivery-package-design.md` / `delivery-package-checklist.md` | 交付包设计 |
| `pricing-and-offer-notes.md` | 定价备注 |
| `buyer-onboarding-flow.md` | 买家上手 |
| `refund-and-support-boundary.md` | 退款与支持边界 |
| `multi-ide-delivery-notes.md` | 多 IDE 差异 |
| `prelaunch-gate.md` | 上线总门禁 |

### 代码

| 文件 | 说明 |
| --- | --- |
| `src/novel_suite/core/commercialization.py` | `validate_commercial_review()` |
| `src/novel_suite/cli.py` | `commercial-review validate` |
| `src/novel_suite/core/errors.py` | C6/C7 错误码 |
| `src/novel_suite/core/product_layer.py` | `product validate` 增加 C6/C7 关键文件 |
| `tests/test_video_production_commercial_review.py` | 7 项测试 |

---

## 上下文缺口记录

- 提示词引用 `quality/scorecards/video_quality_scorecard.md` **不存在**；已映射至 `quality/definitions/quality_scorecard.md`（记入
`quality-gate-review.md` 与 blocker B10）。

---

## C6 结论

| 项 | Verdict |
| --- | --- |
| `cold_case_echo_short_drama` | 虚构演示样例，`demo_only` |
| 资产权利 | C6 manifest 字段齐全；遗留 `handoff/asset_manifest.sample.json` 缺字段 → **B05 blocker** |
| Prompt 原创性 | 抽样为自有虚构；须全量人工复核 → **B06** |
| Adapter | 仅 dry-run，`blocked` 用于生产执行 |
| 质量 | 引用 scorecard/taxonomy/repair；无真实成片 → `blocked` 商业交付 |
| **C6 总 verdict** | `demo_only`（演示）/ `blocked`（商业发布） |

---

## C7 结论

| 项 | 说明 |
| --- | --- |
| 允许 claims | 流程编排、五级包、质量框架、Rules Pack、product/dry-run 演示 |
| 禁止 claims | 一键成片、爆款保证、默认第三方调用、已可商业发布 |
| 交付包 | 四层分离；默认不含模型/密钥/账号/成片 |
| 多 IDE | 薄适配入口；不承诺五端一致 |
| **Prelaunch** | `blocked` — 销售页付费上线仍禁止 |

---

## 允许 / 禁止 Claims 摘要

**允许：** 工作流与契约、质量评分与返修框架、只读 product layer、默认关闭 dry-run adapter。  
**禁止：** 高质量一键成片、收益/平台/版权保证、默认云服务与 NLE、商业发布已合规。

---

## 当前 Release Blockers（P0）

1. **B01** — 法律复核未完成（`COMMERCIAL_RELEASE_GATE.md` §6）
2. **B02** — 商业发布门禁默认「不允许」
3. **B03** — 无真实成片，仅规格样例
4. **B04** — Adapter 仅 dry-run，真实执行须 C8
5. **B05** — 遗留 handoff manifest 权利字段不全

**商业发布：** **仍禁止**

---

## 测试

| 命令 | 结果 |
| --- | --- |
| `pytest tests/test_video_production_commercial_review.py -q` | **7 passed** |
| `pytest tests/test_video_production_adapters.py -q` | **11 passed** |
| `novel-suite product validate --json` | ✅ `PRODUCT_VALIDATE_OK` |
| `novel-suite commercial-review validate --json` | ✅ `COMMERCIAL_REVIEW_VALIDATE_OK` |
| `pytest -m "not ffmpeg"` | **443 passed**, 2 skipped |

---

## 未执行动作

- 未调用外部服务或专业软件
- 未执行 FFmpeg
- 未启用真实 adapter
- 未修改 SOLO / Reasonix
- 未发布 / 上传 / 外发
- 未将商业发布状态改为允许

---

## 下一阶段建议

1. **C8：** 真实 adapter 启用前安全评审（须人工确认）
2. **C9：** 商业候选包打包清单与最终门禁
3. **C10：** 多 IDE 用户试用脚本与反馈回收包
