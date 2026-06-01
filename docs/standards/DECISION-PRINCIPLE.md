# 决策呈现原则

**版本：** 1.0（2026-05-31，由协作实践沉淀）  
**Cursor 规则：** [.cursor/rules/agent-decision-principle.mdc](../../.cursor/rules/agent-decision-principle.mdc)
（`alwaysApply: true`）

---

## 背景

当 Agent 把多个技术方案（A/B/C）直接抛给用户选择时，非专业用户难以判断「怎样对项目最有利」，容易拖延或误选。本原则要求 **Agent 完成对比分析并给出单一推荐**，用户 **只确认或否决**，不充当架构师角色。

---

## 原则

| 角色 | 职责 |
| --- | --- |
| **Agent** | 对比利弊 → 对照参考项目/审计/环境 → 给出一条推荐方案 → 说明理由 |
| **用户** | 回复「确认」或「不确认 + 原因」 |

---

## Agent 输出模板

1. **对比表**（可选路径 × 好处 × 风险）  
2. **推荐结论**（一句话 + 依据）  
3. **请确认块**（合并为一条方案，非多选题）

---

## 已确认案例（2026-05-31）

| 决策项 | 推荐结论 | 用户 |
| --- | --- | --- |
| Skill 脚本架构 | Option A：engine 保留实现，skill 薄 wrapper | 已确认 |
| demo-novel 范围 | 3 人物 + 2 地点 + 1 世界观 + 1 弧 + 1 章 | 已确认 |
| 实施顺序 | 先 P0（bug + tmp），再 P1（wrapper + demo） | 已确认 |

---

## 反模式

- 「你需要在以下三项中选一项……」  
- 「如果不确定可以都试试」  
- 把 ROADMAP 优先级完全交给用户排序而不给建议  

---

*与 [STRUCTURE-STANDARDS.md](./STRUCTURE-STANDARDS.md)、[POST-CODE-VERIFICATION.md](./POST-CODE-VERIFICATION.md) 同属仓库协作规范。*
