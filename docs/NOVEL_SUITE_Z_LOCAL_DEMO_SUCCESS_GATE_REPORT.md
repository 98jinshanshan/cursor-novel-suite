# Novel Suite Z 本地 Demo 闭环验收报告

**日期：** 2026-06-01  
**范围：** Z1 验收文档 · Z2 OpenClaw Y4 语义修复 · Z3 Mobile/App 前期规划

---

## Z1 — Demo Success Gate

| 交付物 | 路径 |
| --- | --- |
| 验收门 | `novel-suite/ui-agent-workbench/demo_success_gate.md` |
| 成功结论（仅此） | **本地 UI Agent Workbench Demo 闭环成立** |

### 四入口体验路径

```text
Doctor → 市场调研 demo → IP 转短剧 demo → novel.review demo
```

### 三业务 Agent 闭环

```text
市场调研 demo → ip.to_short_drama → novel.review
```

## Z2 — 语义修复（OpenClaw Y4 backlog）

| CR-ID | 修复 |
| --- | --- |
| CR-Y4-001 | `release.preflight` → `planned-but-blocked`；新增 `menu_items/release.preflight.json` |
| CR-Y4-002 | UI 侧栏 vs manifest 6 项统计分表（capability_menu、index.html legend） |
| CR-Y4-003 | demo_success_gate 明确双路径定义 |
| CR-Y4-004 | 审稿结果旁「改稿建议需人工采用，不自动写回」 |
| CR-Y4-005 | 文档声明 Z 不扩 `asset.manage` |

## Z3 — Mobile/App 前期规划

| 交付物 | 路径 |
| --- | --- |
| 规划文档 | `novel-suite/ui-agent-workbench/mobile_app_readiness_plan.md` |
| 路线 | Z → AA Mobile-Ready PWA → AB App Shell |
| 明确不做 | 登录、支付、云同步、上架、真实视频 |

## 验证

| 命令 | 结果 |
| --- | --- |
| agent-entry-menu validate/list | OK |
| server validate | OK |
| ip-production-demo validate/run | OK |
| novel-review-demo validate/run | OK |
| product validate | OK |
| commercial-release-candidate | verdict=blocked |
| pytest z_stage | 见执行回执 |

## 边界

- `commercial_release_allowed=false` · `verdict=blocked` 未改
- 未实现 App/PWA/登录/支付
- 未扩 `asset.manage` / 真实 `release.preflight`

## 不可宣布

商业发布、收费销售、真实视频、平台发布、法律/版权通过、App 可上架、自动改稿写回。
