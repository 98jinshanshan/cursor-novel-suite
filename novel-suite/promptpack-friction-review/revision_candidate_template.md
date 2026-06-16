# 修订候选模板（不自动应用）

将真实卡点转为修订候选时，须标注修改类型（**不**直接改 `prompt-packs/` 原文）。

## 修改类型（必选其一或多）

| 类型 | 说明 | 示例 |
| --- | --- | --- |
| 文案澄清 | 消除歧义表述 | 「首章目标」定义更具体 |
| 输入字段补充 | 增加必填/可选字段说明 | 补充「受众」示例 |
| 输出格式补充 | 规范输出结构 | 增加故事圣经章节标题 |
| 边界声明增强 | 强调 demo/blocked | 重申不可商业发布 |
| 示例补充 | 增加虚构短例 | 见 input_output_examples 风格 |

## 候选记录

```markdown
## CR-PP-XXX

- promptpack_id: PP-001
- change_type: 文案澄清
- current_text_ref: （章节/段落引用，非全文粘贴）
- proposed_change_summary:
- priority: P1
- revision_candidate_only: true
- auto_promptpack_changed: false
```

R2 阶段再评审是否合并进 PromptPack。
