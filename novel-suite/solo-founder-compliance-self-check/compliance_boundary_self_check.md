# 合规边界自查（个人开发者）

## 性质

这是**个人开发者合规自查**，不是法律意见。AI 不生成法律结论。

## 自查项

| 项 | 结论 |
| --- | --- |
| 是否已取得律师书面意见 | 否 → B01 保持 open |
| 是否有真实商业成片 | 否 → B03 保持 open |
| 真实 adapter 是否已启用 | 否 → B04 保持 open |
| 素材权利是否商业可用 | 否 → B05 仅 `resolved-demo-only` |
| `legal_conclusion_auto_generated` | 固定 `false` |
| `auto_blocker_closure` | 固定 `false` |

## 允许继续

本地 demo、文档打磨、PromptPack 优化、试用反馈收集 — 在 `verdict=blocked` 前提下均可继续。

## 禁止

- 声称“已律师审核”“已版权安全”“已商业可用”
- 自动关闭 B01–B04
- 将 B05 升级为商业权利已批准
