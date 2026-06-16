# Agent 禁止创建 Tag（O2 替代）

```yaml
agent_may_create_tag: false
tag_created: false
```

## 规则

- Agent **不得**执行 `git tag`、打版本号、创建 release 资产
- 即使负责人本地手动打 tag，也**不**代表商业发布已批准
- 任何 tag/zip/release 须等待真实商业发布流程与法律复核

## 与 N2 冻结填报包的关系

`freeze-decision-fill-kit` 面向团队式冻结决议填报；本包面向**个人开发者自查**，二者均保持 `verdict=blocked`。
