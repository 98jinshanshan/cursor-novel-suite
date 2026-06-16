# 节点执行契约（NEC）

**版本：** 1.0（2026-06-02）  
**适用范围：** Novel Suite 全部 Phase 0–9 与视频 V0–V2  
**依据：** [AGENTS.md](../../AGENTS.md) Agent-first、[STRUCTURE-STANDARDS.md](./STRUCTURE-STANDARDS.md) Option
A、[workflow-validation-synthesis](../audit/2026-06-01-workflow-validation-synthesis.md)

---

## 1. 问题与目标

用户以自然语言进入某 Phase（例：「搜集各大平台最火短视频」）时，**IDE 内 Agent** 必须：

1. 读取该 Phase 的 Skill **NEC 分派表**
2. 将意图拆解为子任务 ID（`P0-S1` …）
3. 将每个子任务路由到 **CLI 脚本** 或 **Agent+reference**
4. 产出 **落盘产物** + **完成清单（Completion Manifest）**
5. 在对话框给出 **摘要**（不得替代落盘）

**加厚 1→10** 的主战场是此「节点内编排层」，而非 SOLO 或单一 CLI 命令。

---

## 2. NEC 七段结构（每个 Phase Skill 必备）

| 段 | 内容 |
| --- | --- |
| **1 Entry Triggers** | 启动本节点的自然语言示例 |
| **2 Intent Decomposition** | 用户话 → 标准子任务 ID |
| **3 Dispatch Table** | 子任务 → 执行体（`scripts/*.py` / Agent+reference） |
| **4 Execution Order** | 依赖、可并行项 |
| **5 Output Contract** | 必落盘路径 |
| **6 Chat Summary** | 对话框必报字段 |
| **7 Gate Handoff** | `pipeline gate` / manifest 校验项 |

详细分派表放在 `skills/<name>/references/node-dispatch.md`；`SKILL.md` 内保留 NEC 摘要并链到该文件。

---

## 3. 执行体类型

| 类型 | 说明 |
| --- | --- |
| `cli` | Agent 调用 `novel_cli.py` / `video_cli.py` 或 skill `scripts/` wrapper |
| `agent` | Agent 按 reference 执行（搜索、写作、填表），结果写入指定 md/json |
| `hybrid` | CLI 打底稿 + Agent 按模板补全（Phase 0 fiction 平台节） |

**禁止：** 仅在对话中输出表格/结论而不写 manifest 与契约路径（视为节点失败）。

---

## 4. Completion Manifest

### 4.1 路径约定

| 范围 | 路径 |
| --- | --- |
| Phase 0（套件级） | `intel/radar/YYYY-Www.completion.json` |
| Phase 1–9（单书） | `novels/<slug>/canon/nodes/phase-N.completion.json` |
| 视频 job | `cursor-novel-video/tmp/video_jobs/<id>/node.completion.json` |

### 4.2 Schema

`cursor-novel-writer/schema/node-completion.schema.json`

校验：`python engine/novel_cli.py node validate --phase N [--project ...]`

### 4.3 状态

- `complete` — 全部必做子任务 `done`
- `partial` — 进行中；**禁止** `pipeline gate` 通过
- 子任务 `status`：`pending` | `done` | `skipped` | `failed`

---

## 5. 对话框 vs 落盘

| 内容 | 落盘 | 对话框 |
| --- | --- | --- |
| 雷达全文、审稿报告、章节正文 | ✅ | 仅摘要 |
| Top3 题材、open blockers | ✅（manifest 记录） | ✅ 必报 |
| 用户确认「选题材②」 | ✅ 写入 concept-brief / manifest | ✅ 复述 |

---

## 6. 与 novel-pipeline 关系

- **宏观路由：** `novel-pipeline` → delegate 原子 Skill
- **微观执行：** 原子 Skill 的 NEC + `node-dispatch.md`
- 进入 Phase N 前：Agent **必须先 Read** 该 Phase Skill 的 NEC 段

---

## 7. 多 IDE

NEC 写在 canonical 源目录：

- `cursor-novel-writer/skills/`
- `cursor-novel-video/skills/`

经 `platforms/install-skills.ps1` 同步至各 IDE 的 **隐藏安装目录**（见 [WORKSPACE-LAYOUT.md](./WORKSPACE-LAYOUT.md)）。三端行为一致。

---

*矩阵与成熟度：[plans/NEC-10-enrichment-matrix.md](../plans/NEC-10-enrichment-matrix.md)*
