# Blocker 保留记录（O3 替代）

与 [known-blockers.md](../commercial-release-candidate/known-blockers.md) 对齐。

| ID | 状态 | 个人开发者阶段说明 |
| --- | --- | --- |
| B01 | **open** | 无律师复核；`legal_review_completed=false` |
| B02 | **open** | 商业发布门禁不允许 |
| B03 | **open** | 无真实成片 |
| B04 | **open** | 真实 adapter 执行 blocked |
| B05 | **resolved-demo-only** | demo 字段已补齐；**仍须人工权利复核** |

## 固定字段

```yaml
auto_blocker_closure: false
legal_conclusion_auto_generated: false
commercial_release_allowed: false
verdict: blocked
```

个人开发者自查**不**关闭上述 blocker。解除路径仍见 `final-release-gate.md`。
