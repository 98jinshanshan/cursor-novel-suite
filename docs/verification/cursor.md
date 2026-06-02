# Cursor 平台 — Agent 对话与 smoke 验证

**状态：** Cursor 侧 NEC 验收已完成（2026-06-03）  
**主入口：** [AGENTS.md](../../AGENTS.md)  
**统一验收表：** [NEC-smoke-matrix.md](./NEC-smoke-matrix.md)

## 一次性安装

在 **Novel Suite 根**（含 `.novel-suite-root`）：

```powershell
powershell -File platforms/install-skills.ps1 -Agents cursor
py -3 cursor-novel-writer/engine/novel_cli.py suite doctor --agents cursor
```

可选：去掉旧双份安装（仅保留 `.cursor/skills`）：

```powershell
Remove-Item -Recurse -Force .agents\skills -ErrorAction SilentlyContinue
```

或 `npx skills add ./cursor-novel-writer -a cursor -y`（+ video）。

**工作区：** 推荐 [novel-suite.code-workspace](../../novel-suite.code-workspace)。  
**编辑源：** `cursor-novel-writer/skills/`、`cursor-novel-video/skills/`（不要改 `.cursor/skills` 镜像）。

## 引擎一键 smoke（Cursor 已跑通）

```powershell
py -3 cursor-novel-writer/engine/scripts/nec_cursor_smoke.py --out docs/verification/cursor-nec-run-latest.json
py -3 cursor-novel-video/engine/scripts/nec_video_smoke.py
```

| 脚本 | 预期 |
| --- | --- |
| `nec_cursor_smoke.py` | 退出码 0，`gaps: []` |
| `nec_video_smoke.py` | 退出码 0，`status: complete` |

机器记录：[cursor-nec-run-latest.json](./cursor-nec-run-latest.json)

## NEC 分步（与矩阵一致）

| 步骤 | 命令 | 预期 |
| --- | --- | --- |
| 1 | `novel suite doctor --agents cursor` | 全 OK（可有 `skills_cursor_dual_install` WARN） |
| 2 | `intel_scan.py --demo` | `intel/radar/*.completion.json` **complete** |
| 3 | `novel node sync --phase 1..9 --project examples/demo-novel` | 10 个 manifest，无 pending |
| 4 | `novel pipeline gate --phase 6 --project examples/demo-novel` | GATE OK |
| 5 | `novel export --project examples/demo-novel` | `dist/*.epub` |

## Agent 对话（主路径）

见 [NEC-smoke-matrix.md](./NEC-smoke-matrix.md) §Agent 对话 smoke。

## 检查项（Cursor 实测）

| 项 | 结果 | 日期 |
| --- | --- | --- |
| `suite_version` ≥ 2026.06.03-nec | ✅ | 2026-06-03 |
| `layout_version` 2.0.0 | ✅ | 2026-06-03 |
| install → `.cursor/skills` 13 项 | ✅ | 2026-06-03 |
| `nec_cursor_smoke` gaps 空 | ✅ | 2026-06-03 |
| `nec_video_smoke` | ✅ | 2026-06-03 |
| pytest（not ffmpeg） | ✅ 38 passed | 2026-06-03 |
| pyright | ✅ | 2026-06-01 |

## 排障

| 现象 | 处理 |
| --- | --- |
| 左侧四套 skills | 重载窗口；见 [WORKSPACE-LAYOUT.md](../standards/WORKSPACE-LAYOUT.md) |
| doctor 双份 WARN | 删 `.agents/skills` 或安装时不要 `-AlsoAgents` |
| 找不到 skill | 打开 Suite 根 + `install-skills.ps1 -Agents cursor` |
| manifest 有 pending | `novel node sync --phase N` 后 `node validate --phase N` |

## GitHub 更新（已克隆仓库）

```powershell
git pull origin main
powershell -File platforms/patch-update.ps1 -SkipPull -Agents cursor
```

无 git：`platforms/zip-refresh.ps1` 后同上（`-SkipPull`）。
