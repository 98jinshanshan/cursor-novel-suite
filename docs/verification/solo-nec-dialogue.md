# SOLO / TRAE — NEC 专业对话设计（测试用）

**版本：** 2026-06-03（对齐 `suite-version=2026.06.03-nec`、GitHub CI 已通过）  
**前置：** [solo-clone-checklist.md](./solo-clone-checklist.md) · [NEC-smoke-matrix.md](./NEC-smoke-matrix.md)  
**仓库：** <https://github.com/98jinshanshan/cursor-novel-suite>（`main` ≥ `6bf706a`）

---

## 1. 测试目标（SOLO 要证明什么）

| 层级 | 证明内容 |
| --- | --- |
| 同步 | 从 GitHub 拉到与 Cursor 同版的 NEC 引擎与 Skills |
| 引擎 | `suite doctor`、`nec_*_smoke`、pytest 与 Cursor/GitHub CI 一致 |
| Agent | 能 **Read Skill + 代跑 CLI**，产出落盘路径（非口头表格） |
| NEC | Phase 0 radar manifest、`demo-novel` 的 `phase-*.completion.json` 无 pending |

---

## 2. 人工准备（SOLO 外，一次性）

```powershell
# 在 SOLO 机器、Novel Suite 根目录（含 .novel-suite-root）
powershell -File platforms/solo-sync.ps1 -UseZip -Agents trae-cn
# 或同机：powershell -File platforms/solo-sync.ps1 -Source G:\CURSOR -Agents trae-cn
```

确认：

- IDE 工作区 = **monorepo 根**（不是 `cursor-novel-writer/` 子夹）
- `.trae/skills/` 共 **13** 项（含 `novel-market-scan`、`novel-pipeline`）
- `.novel-suite-root` 中 `suite-version=2026.06.03-nec`

SOLO 自定义 Agent：粘贴 [solo-agent-prompt.md](../../cursor-novel-writer/platforms/trae/solo-agent-prompt.md) 全文为 System Prompt。

---

## 3. System Prompt 补充段（贴在 SOLO Agent 末尾）

```text
【NEC 节点契约 — 2026.06.03】
- 每个 Phase 必须先 Read 对应 SKILL.md 与 references/node-dispatch.md。
- Phase 0 = novel-market-scan（无 phase-0/ 目录）；套件 manifest：intel/radar/*.completion.json。
- 单书 manifest：novels/<slug>/canon/nodes/phase-N.completion.json。
- 执行后必须：代跑 CLI、贴 exit code、给落盘路径；禁止只在对话里给表不写文件。
- 同步验收命令（必须代为运行）：
  py -3 cursor-novel-writer/engine/novel_cli.py suite doctor --agents trae-cn
  py -3 cursor-novel-writer/engine/scripts/nec_cursor_smoke.py
  py -3 cursor-novel-video/engine/scripts/nec_video_smoke.py
- intel 联网失败时用：intel scan --demo（须看到 WARN 离线说明，禁止 mock JSON）。
```

---

## 4. 对话流程（推荐顺序）

### 0 — 工作区门禁（必发）

```text
请确认当前工作区是 Novel Suite 根目录（含 .novel-suite-root、platforms/、cursor-novel-writer/、cursor-novel-video/）。
读取 .novel-suite-root 的 suite-version，要求 ≥ 2026.06.03-nec。
若不是根目录或版本过旧，先说明如何 solo-sync.ps1 -UseZip，不要继续后续步骤。
```

**通过：** Agent 明确根路径 + 版本号。

---

### 1 — 同步与自动化验收（引擎层）

```text
请在本工作区代为执行并原样汇报（含 exit code 与 stderr）：

1) py -3 cursor-novel-writer/engine/novel_cli.py suite doctor --agents trae-cn
2) py -3 -m pytest cursor-novel-writer/tests cursor-novel-video/tests -m "not ffmpeg" -q
3) py -3 cursor-novel-writer/engine/scripts/nec_cursor_smoke.py
4) py -3 cursor-novel-video/engine/scripts/nec_video_smoke.py

要求：
- 任一步 exit≠0 必须贴失败输出并给修复建议，不得写「已通过」。
- nec_cursor_smoke 报告里 gaps 必须为空数组。
- pytest 预期 38 passed（1 deselected）。
```

**通过：**

| 命令 | 预期 |
| --- | --- |
| `suite doctor --agents trae-cn` | 全 OK（`.trae/skills` 13） |
| pytest | `38 passed` |
| `nec_cursor_smoke` | `"gaps": []` |
| `nec_video_smoke` | `"status": "complete"` |

---

### 2 — Phase 0（NEC + Agent）

```text
Phase 0 没有 phase-0/ 目录，唯一 Skill 是 novel-market-scan。请：

1) Read .trae/skills/novel-market-scan/SKILL.md
2) Read .trae/skills/novel-market-scan/references/node-dispatch.md
3) 运行 py -3 cursor-novel-writer/skills/novel-market-scan/scripts/intel_scan.py --demo
4) 运行 py -3 cursor-novel-writer/engine/novel_cli.py node validate --phase 0
5) 读取 intel/radar/ 最新 *.completion.json，汇报 status 与 pending 子任务

对话框只报：Top3 题材摘要 + 两个落盘路径（radar md + completion json）。
```

**通过：** `intel/radar/YYYY-Www.md` + completion `status: complete`（demo 已立项时会回写 P0-S5/S6）。

---

### 3 — demo-novel NEC 节点（Phase 1–9）

```text
请对 cursor-novel-writer/examples/demo-novel 执行 NEC 节点同步与校验：

对 phase=1..9 依次运行：
  novel node sync --phase N --project cursor-novel-writer/examples/demo-novel
  novel node validate --phase N --project ...

再运行：
  novel pipeline status --project ...
  novel pipeline gate --phase 6 --project ...
  novel export --project ...
  novel node sync --phase 9 --project ...

最后列出 canon/nodes/phase-*.completion.json 每个文件的 status，
以及是否还有 pending 子任务。gaps 应为空。
```

**通过：** 10 个 manifest 均为 `complete`，无 `pending`；`pipeline gate --phase 6` → GATE OK。

---

### 4 — 视频 V0（可选）

```text
请 Read video-chapter-summary 的 SKILL.md 与 references/node-dispatch.md，然后：

1) 对 demo 第 1 章（chapters/01_试章.md）生成 9:16 摘要短视频并烧录字幕
2) 若 FFmpeg 不可用，改跑 nec_video_smoke.py 并说明原因
3) 给出 tmp/video_jobs/<id>/node.completion.json 路径与 status

对话框必报：MP4 完整路径、时长、是否带字幕（见 node-dispatch Chat Summary）。
```

**通过：** `node.completion.json` 存在且 `status: complete`，或 smoke 脚本 exit 0。

---

### 5 — 最终验收表（填矩阵用）

```text
请输出 SOLO NEC 验收表（Markdown 表格），列：检查项 | OK/FAIL | 证据路径/命令输出摘要。

必须包含：
- 工作区根 + suite-version
- .trae/skills 数量与 novel-market-scan/scripts/intel_scan.py
- suite doctor --agents trae-cn
- pytest 38 passed
- nec_cursor_smoke gaps=[]
- nec_video_smoke
- intel/radar completion complete
- demo-novel phase-0..9 manifest 无 pending
- pipeline gate phase 6
- Phase 0 对应 novel-market-scan（不是 phase-0 目录）

若有 FAIL，单独一节「修复命令」，不要混在 OK 里。
```

测试完成后，把表中 SOLO 列抄到 [NEC-smoke-matrix.md](./NEC-smoke-matrix.md)。

---

## 5. 一条总任务（省事版）

```text
你是 Novel Suite SOLO 测试员。工作区必须是 monorepo 根，suite-version≥2026.06.03-nec。

严格顺序执行并汇报（代跑命令，贴 exit code）：
【A】suite doctor --agents trae-cn → pytest not ffmpeg → nec_cursor_smoke → nec_video_smoke
【B】Read novel-market-scan + node-dispatch → intel_scan --demo → node validate --phase 0
【C】demo-novel：node sync+validate phase 1-9 → pipeline status → gate phase 6 → export → sync phase 9
【D】可选：demo 第1章 9:16 summary 视频或说明 FFmpeg 限制
【E】输出 SOLO NEC 验收表

约束：Phase 0 必须先 Read novel-market-scan；禁止 mock 雷达；失败必须贴 stderr。
参考：docs/verification/solo-nec-dialogue.md
```

---

## 6. 纠偏话术

| 现象 | 复制发送 |
| --- | --- |
| 跳过 Phase 0 | 仓库无 phase-0/，请先 Read novel-market-scan 再 intel scan，不要写章。 |
| 只给命令不执行 | 请代为运行 CLI 并贴 exit code 与产物路径，不要让我手敲。 |
| mock 雷达 JSON | 请用官方 intel scan --demo，输出须含 WARN 离线 fixture。 |
| 说通过但无文件 | 请列出 intel/radar/*.md 与 canon/nodes/phase-*.json 的真实路径。 |
| 子目录工作区 | 请打开含 .novel-suite-root 的根目录，不是 cursor-novel-writer  alone。 |

---

## 7. 与 Cursor / GitHub 对照

| 项 | Cursor（已测） | SOLO（你填） |
| --- | --- | --- |
| 同步源 | `git push main` | `solo-sync -UseZip` |
| doctor | `--core-only` 或 `--agents cursor` | `--agents trae-cn` |
| pytest | 38 passed | 待填 |
| nec smoke | gaps `[]` | 待填 |
| Agent Read Skill | 对话 smoke | 本设计第 2–4 步 |

GitHub Actions 与 SOLO 引擎层应对齐；SOLO 额外验证 **Agent 是否 Read Skill 并落盘**。

---

## 8. 成功标准速查

```text
✅ solo-sync 无报错
✅ suite-version=2026.06.03-nec
✅ .trae/skills = 13
✅ pytest 38 passed
✅ nec_cursor_smoke → gaps: []
✅ nec_video_smoke → complete
✅ intel/radar/*.completion.json → complete
✅ demo canon/nodes/phase-*.completion.json → complete, 无 pending
✅ Agent 明确 Phase 0 = novel-market-scan
```

---

## 9. 写书话术

从选题到第一章：[solo-phase0-to-ch01-dialogue.md](./solo-phase0-to-ch01-dialogue.md)
