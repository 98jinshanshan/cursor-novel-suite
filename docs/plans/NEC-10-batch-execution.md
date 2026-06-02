# NEC-10 批量执行计划（无需逐 Phase 再确认）

**用户已于 2026-06-02 回复「确认」整包 NEC-10。** 此后 Agent **不得** 每完成一个 Phase 就停下来索要确认。

---

## 执行模式

| 规则 | 说明 |
| --- | --- |
| 用户确认 | **仅一次**（整包 NEC-10） |
| Agent 推进 | 按下列批次连续改仓，批次间 **不** 打断用户 |
| 汇报节奏 | **每批次结束** 汇报：改了什么、pytest/Problems、**下一批次名称** |
| 问题栏 | 每批次结束必跑 ReadLints + 相关 pytest，**清零后才能称批次完成** |

---

## 批次 A — 已完成（2026-06-02）

- [x] NEC-0 标准 + schema + `node_completion.py`
- [x] NEC-1 Phase0 样板（分派表、manifest、gate、intel scan）
- [x] NEC-2–6 分派表 v1（各 Skill `node-dispatch.md`）
- [x] 目录导航 `docs/workflow/`、`skills/README.md`
- [x] 工作区左侧：`WORKSPACE-LAYOUT.md` + `.vscode` 隐藏 IDE 安装镜像

---

## 批次 B — Phase 1–3 引擎 manifest（✅ 2026-06-03）

| 任务 | 交付 | 状态 |
| --- | --- | --- |
| B1 | `novel init` → `phase-1.completion.json` | ✅ |
| B2 | `novel node sync --phase 2/3` + gate≥4 校验 manifest | ✅ |
| B3 | worldbuilding / character / plot SKILL NEC 顶栏 | ✅ |
| B4 | pytest `test_batch_b_node_sync_phase2_3_demo` | ✅ |

**验证命令：**

```powershell
py -3 cursor-novel-writer/engine/novel_cli.py node sync --phase 2 --project examples/demo-novel
py -3 cursor-novel-writer/engine/novel_cli.py node sync --phase 3 --project examples/demo-novel
Get-ChildItem cursor-novel-writer/examples/demo-novel/canon/nodes/
```

---

## 批次 C — Phase 4–8 manifest（✅ 2026-06-03）

| 任务 | 交付 | 状态 |
| --- | --- | --- |
| C1 | `novel node sync --phase 4-8` | ✅ |
| C2 | gate≥5 校验 phase-4 … gate≥9 校验 phase-8 | ✅ |
| C3 | `templates/references/phase-4-node-dispatch.md` | ✅ |
| C4 | `novel-review` NEC + demo snapshot + pytest | ✅ |

**验证：**

```powershell
py -3 cursor-novel-writer/engine/novel_cli.py node sync --phase 6 --project examples/demo-novel
Get-ChildItem cursor-novel-writer/examples/demo-novel/canon/nodes/phase-*.completion.json
```

---

## 批次 D — Phase 9 + 视频（✅ 2026-06-03）

| 任务 | 交付 | 状态 |
| --- | --- | --- |
| D1 | `novel node sync --phase 9` + phase-9 manifest | ✅ |
| D2 | `video_node_completion.py` + summary 成功写 `node.completion.json` | ✅ |
| D3 | video / novel-export NEC 顶栏 | ✅ |
| D4 | pytest batch_d + video completion | ✅ |

---

## 批次 E — 三 IDE 验收（✅ 2026-06-03）

| 任务 | 交付 | 状态 |
| --- | --- | --- |
| E1 | [NEC-smoke-matrix.md](../verification/NEC-smoke-matrix.md) | ✅ |
| E2 | cursor / qoder / trae-cn 对齐矩阵 | ✅ |
| E3 | docs/INDEX 链接 | ✅ |

**NEC-10 全部批次已完成。**

---

## 目录架构（物理 vs 可见）

| 动作 | 状态 |
| --- | --- |
| 隐藏整夹 `.agents/.qoder/.trae` | ✅ layout 2.0.0 `.vscode` |
| 架构权威文档 | ✅ `DIRECTORY-ARCHITECTURE.md` + `layout-phase-map.json` |
| 多根工作区 | ✅ `novel-suite.code-workspace` |
| 把 skills 挪到 repo 根 | **不做** |

---

*ROADMAP 见 [ROADMAP.md](./ROADMAP.md) P6。*
