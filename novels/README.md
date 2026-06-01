# 用户小说工程目录

每本书一个子目录，**禁止**把多本小说的章节/reviews/snapshots 混在同一文件夹。

| 文件 | 作用 |
| --- | --- |
| `_registry.json` | 全部小说登记（slug、路径、platform） |
| `.active` | 当前活动小说 slug |
| `<slug>/` | 单本书完整工程（见 STRUCTURE-STANDARDS §3.1） |

新建（须先 Phase 0 选品，见 `novel-market-scan`）：

```powershell
# 在 Novel Suite 根目录（含 .novel-suite-root，路径任意）
py -3 cursor-novel-writer/engine/novel_cli.py suite doctor
# 1. Agent 运行 novel-market-scan → intel/radar/YYYY-Www.md
# 2. 确认 concept → intel/concepts/<slug>.md
py -3 cursor-novel-writer/engine/novel_cli.py init --title "书名" --premise "梗概" --concept ./intel/concepts/<slug>.md
py -3 cursor-novel-writer/engine/novel_cli.py pipeline gate --phase 1
```

默认创建到 `novels/<auto-slug>/` 并设为活动书。

示例工程仍在 `cursor-novel-writer/examples/demo-novel/`（不参与 registry 污染）。
