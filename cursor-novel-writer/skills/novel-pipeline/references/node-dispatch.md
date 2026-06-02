# 总控节点路由（novel-pipeline）

**宏观 NEC：** 用户意图 → Phase N → **必须先 Read** 对应原子 Skill 的 `references/node-dispatch.md`。

## Phase → Delegate

| Phase | Skill | 完成清单 |
| --- | --- | --- |
| 0 | `novel-market-scan` | `intel/radar/*.completion.json` + 项目 `phase-0.completion.json` |
| 1 | `story-init` | `canon/nodes/phase-1.completion.json` |
| 2 | `worldbuilding` + `character-management` | `phase-2.completion.json` |
| 3 | `plot-structure` | `phase-3.completion.json` |
| 4 | voice-brief（模板） | `phase-4.completion.json` |
| 5 | `chapter-writing` | `phase-5.completion.json` |
| 6–8 | `novel-review` | `phase-6`…`phase-8.completion.json` |
| 9 | `novel-export` | `phase-9.completion.json` |

## 执行顺序

```text
Read novel-pipeline → resolve active project → Read phase Skill NEC → execute dispatch → node validate → pipeline gate
```

## Chat Summary

当前 Phase、delegate Skill 名、completion 路径、gate 结果。
