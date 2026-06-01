# Repair Action Spec — 第{{N}}章

> Forge 阶段 3 输出模板（PW-07）。保存为 `reviews/ch{{NN}}-repair.md` 或并入 `reviews/ch{{NN}}-review.md`。

## 元信息

| 字段 | 值 |
| --- | --- |
| 章节 | chapters/{{NN}}_*.md |
| 轮次 | round {{1}} / 2 |
| 平台 | {{platform_target}} |

## Action Spec

| ID | 严重度 | 位置 | 问题 | 动作 | 状态 |
| --- | --- | --- | --- | --- | --- |
| R01 | blocker | §段落/行 | （描述） | （具体改法） | open |
| R02 | warn | | | | open |
| R03 | nit | | | | open |

**严重度：** `blocker` → 必须改；`warn` → 建议改；`nit` → 可选。

**动作动词：** 删 / 增 / 移 / 改 POV / 改时间 / 补铺垫 / 改对话 / de-AI 替换。

## 执行顺序

1. 全部 blocker（结构、一致性）
2. warn（节奏、对话、文风）
3. nit（可选 polish）
4. De-AI 表（Phase 7）
5. `novel promote {{NN}}_标题.md` → 再验证

## 完成检查

- [ ] 所有 blocker = done
- [ ] 修订稿在 `chapters/.drafts/`
- [ ] 已 promote 并重跑 Phase 6/8
