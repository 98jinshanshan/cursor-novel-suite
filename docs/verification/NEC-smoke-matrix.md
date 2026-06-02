# NEC 多 IDE 验收矩阵（统一）

**日期：** 2026-06-03  
**契约：** [NODE-EXECUTION-CONTRACT.md](../standards/NODE-EXECUTION-CONTRACT.md)  
**安装：** 根目录 `platforms/install-skills.ps1`（源：`cursor-novel-*/skills/`）

---

## 引擎自检（三端相同）

```powershell
py -3 cursor-novel-writer/engine/novel_cli.py suite doctor
py -3 cursor-novel-writer/engine/novel_cli.py node sync --phase 9 --project cursor-novel-writer/examples/demo-novel
```

| 检查项 | 预期 |
| --- | --- |
| `layout_version` | `layout 2.0.0 OK` |
| `suite_version` | ≥ `2026.06.03-nec` |
| demo `phase-0`…`phase-9.completion.json` | 存在且 `status: complete`（Phase9 需先 export） |

---

## 引擎一键 smoke

```powershell
py -3 cursor-novel-writer/engine/scripts/nec_cursor_smoke.py
py -3 cursor-novel-video/engine/scripts/nec_video_smoke.py
```

---

## Agent 对话 smoke（复制到各 IDE）

| 步骤 | 输入话术 | 预期落盘 |
| --- | --- | --- |
| 0 | 请运行 novel suite doctor 并解读 | 全 OK |
| 1 | 读取 novel-market-scan 的 node-dispatch，执行 intel scan --demo | `intel/radar/*.completion.json` |
| 2 | 对 examples/demo-novel 运行 node sync --phase 1 到 8 | `canon/nodes/phase-*.json` |
| 3 | 按 novel-pipeline 显示 pipeline status | Phase 列表 |
| 4 | 导出 demo-novel EPUB 后 node sync --phase 9 | `dist/*.epub` + `phase-9.completion.json` |
| V0 | 把 demo 第1章做成 9:16 摘要视频（可 --dry-run 若无 FFmpeg） | `tmp/video_jobs/*/node.completion.json` |

---

## 平台实测列

| 步骤 | Cursor | Qoder | TRAE-CN |
| --- | --- | --- | --- |
| install-skills.ps1 | ✅ `.cursor/skills` 13；`2026-06-03` | 待填 | 待填 |
| Phase0 intel --demo | ✅ complete（demo 回写）；`2026-06-03` | 待填 | 待填 |
| node sync 1–9 | ✅ gaps 空；`2026-06-03` | 待填 | 待填 |
| pipeline gate 6 | ✅ GATE OK；`2026-06-03` | 待填 | 待填 |
| video summary job | ✅ `nec_video_smoke.py`；`2026-06-03` | 待填 | 待填 |

**Cursor 记录：** [cursor-nec-run-latest.json](./cursor-nec-run-latest.json) · [cursor.md](./cursor.md)

---

## 链接

- [cursor.md](./cursor.md)
- [qoder.md](./qoder.md)
- [trae-cn.md](./trae-cn.md)
- [solo-clone-checklist.md](./solo-clone-checklist.md)（仅 TRAE 部署变体）
