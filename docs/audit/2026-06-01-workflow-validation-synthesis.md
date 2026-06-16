# 第三层：Workflow 与验证专项合成分析

**日期：** 2026-06-01  
**前置：** [第二层交叉审计](./2026-05-31-reference-crosswalk.md) · [结构合规](./2026-05-31-structure-compliance.md)  
**状态：** 已实施（见 [ROADMAP](../plans/ROADMAP.md) P3 节）

---

## 1. 问题陈述

用户期望 **插件式全流程**（立项→世界观→写作→验证→修订→再验证→导出），而非 11 个分散 Skill 靠 Agent 自觉串联。验证节点需包含：**设定一致性 + 去 AI 味 + 自然语言文风契约**，且借鉴须来自 12
个参考项目的成熟设计，非临时补丁。

---

## 2. 十二参考源 × 六维度精华对照

| 维度 | 精华设计（参考源） | 我们原状 | 合成决策 |
| --- | --- | --- | --- |
| **A 编排** | novel-skill 五阶段；zencoder 7 Agent 流水线 | 8 原子 Skill，无总控 | ✅ 新增 `novel-pipeline` 编排，**delegate** 现有 Skill |
| **B 目录** | story-skills 注册表；Novel Master 快照；postwriter canon 门控 | task_plan 简化 | ✅ 扩展 `task_plan.md` 阶段门控 + `canon/voice-brief.md` |
| **C 验证→修订** | postwriter PW-11 先 validate 再 rewrite；Forge 合成 | checklist 无 enforce | ✅ forge 阶段 4–5：de-AI + re-validate（最多 2 轮） |
| **D 去 AI / 文风** | zencoder **Sable** copy edit；Ghostlight 冷读；Workshop Reader Test | 无专门 reference | ✅ `deai-checklist.md` + persona prompts + voice-brief |
| **E 图谱** | graphify init/review/update/query | bridge 已有 | ⚠️ pipeline 在写作后/审稿前插入 update |
| **F 小说→视频** | video_skills 触发表；super-video job_state | 章节 md 约定已有 | ➖ 本层不改 video（衔接已在 README） |

### 2.1 刻意不借

| 参考 | 不借原因 |
| --- | --- |
| postwriter PostgreSQL / 11 维评分 / repair DB | 过重，与「无 DB」原则冲突 |
| novel-skill RPG 10–15 决策点 | 非中文通用默认路径 |
| zencoder IDE 插件绑定 | 走 agentskills 标准 |
| postwriter 54 literary device 自动检测 | P2 可选，本层用 checklist 代替 |

---

## 3. 目标工作流（门控）

```text
Phase 1 立项 (story-init)
Phase 2 世界观+人物 (worldbuilding + character-management)
Phase 3 大纲 (plot-structure)
Phase 4 文风契约 (voice-brief)          ← Novel Master + zencoder Spark 前置
Phase 5 写作 (chapter-writing)
Phase 6 验证 (novel-review: blocker → personas)
Phase 7 去 AI (Sable + deai-checklist)
Phase 8 再验证 (re-review, max 2 rounds)
Phase 9 导出 (novel-export)
```

**Gate 规则（postwriter PW-11 + forge-workflow 禁止项）：**

- 存在 **blocker** → 禁止 Phase 7/9
- Phase 7 完成 → 必须 Phase 8
- Phase 8 两轮仍 fail → 暂停，报告用户

---

## 4. 实施清单（本次）

| ID | 交付物 | 路径 |
| --- | --- | --- |
| W1 | 总控 Skill | `skills/novel-pipeline/SKILL.md` |
| W2 | 文风契约模板 | `templates/voice-brief.md` |
| W3 | 扩展 task_plan | `templates/task_plan.md` |
| W4 | 去 AI 清单 | `skills/novel-review/references/deai-checklist.md` |
| W5 | 人格 prompts | `skills/novel-review/references/personas/*.md` |
| W6 | Forge 4–5 阶段 | `forge-workflow.md` 更新 |
| W7 | novel-review v1.1 | `SKILL.md` 追加 |
| W8 | CLI pipeline status | `novel_cli.py pipeline status` |
| W9 | demo 示例 | `examples/demo-novel/canon/voice-brief.md` |

---

## 5. 版本兼容

- **不改名**现有 11 Skill；新增 `novel-pipeline` 为第 12 个
- **additive** references；`novel-review` metadata 1.0.0 → 1.1.0
- junction 安装指向源目录 → 更新自动生效；新 Skill 需补 junction（见 `platforms/install.ps1`）

---

*第三层合成完成。实施与 ROADMAP P3 同步。*
