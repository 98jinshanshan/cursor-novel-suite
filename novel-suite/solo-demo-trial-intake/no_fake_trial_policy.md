# No Fake Trial Policy（Q1）

```yaml
fake_feedback_generated: false
trial_executed: false
```

## 规则

- Agent **不得**代填「入口清楚/不清楚」「试跑顺利/不顺利」等体验结论
- Agent **不得**伪造 IDE 名称、耗时、卡点列表
- sample JSON 必须 `sample_only=true`，仅为结构示例
- 真实记录仅来自用户或实际 IDE 会话，保存于 `.tmp/novel-suite-q/solo-demo-trial-intake/`
- 承接前须用户明确授权范围

## 与 P1 关系

P1 提供 15 分钟路线；Q1 承接**真实**试跑结果，不替代试跑本身。
