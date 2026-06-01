# cursor-novel-writer

中文通用小说创作工具包：**Agent Skills（对话主入口）** + **CLI 引擎** + **graphify 一致性**。

- **Agent 对话入口（推荐）：** [../AGENTS.md](../AGENTS.md)
- Monorepo 文档：[../docs/INDEX.md](../docs/INDEX.md)

---

## 怎么用（Agent 对话）

1. 在 IDE 打开 **Novel Suite 根目录**（含 `.novel-suite-root`，非单独子文件夹）
2. 安装 Skills 并自检：

```bash
npx skills add ./cursor-novel-writer -a cursor -a qoder -a trae-cn -y
py -3 cursor-novel-writer/engine/novel_cli.py suite doctor
```

Windows：`powershell -File platforms/install-skills.ps1`（junction 链接，见 monorepo 根）

3. 在 Agent 对话中说：

| 目标 | 示例话术 |
| --- | --- |
| Phase 0 扫榜选题 | `请按 novel-market-scan 执行本周 intel scan，展示 radar Top 题材` |
| 全流程开书 | `按 novel-pipeline：扫榜→我确认 concept→init→gate phase 1` |
| 写下一章 | `对 active 小说续写下一章（chapter-writing）` |
| 审稿 / 导出 | `novel-review 审稿；gate 通过后 export EPUB` |

默认总控 Skill：**`novel-pipeline`**（Phase 0→9）。

---

## Skills（10 个）

| Skill | 用途 |
| --- | --- |
| **`novel-pipeline`** | **全流程总控** |
| **`novel-market-scan`** | **Phase 0 全平台扫榜 + 短视频选题** |
| `story-init` | 立项 |
| `character-management` | 人物与关系 |
| `worldbuilding` | 世界观 |
| `plot-structure` | 大纲、伏笔 |
| `chapter-writing` | 逐章写作 |
| `novel-review` | graphify + 审稿 + 去 AI |
| `novel-export` | EPUB |
| `novel-marketing` | 宣传文案（可选） |

---

## 兼容平台

| 平台 | Skills 目录 |
| --- | --- |
| Cursor | `.agents/skills/` |
| Qoder | `.qoder/skills/` |
| TRAE / SOLO | `.trae/skills/` 或 `~/.trae-cn/skills/` |

一键安装：`powershell -File platforms/install-skills.ps1`（或 `cursor-novel-writer/platforms/install.ps1`）

---

## CLI 附录（引擎层）

与 IDE Agent **同等能力**；通常由 Agent 后台调用。

```bash
pip install -r requirements.txt

py -3 engine/novel_cli.py suite doctor
py -3 engine/novel_cli.py intel scan --period week
py -3 engine/novel_cli.py init --title "雾港来信" --premise "..." \
  --concept ../intel/concepts/<topic>.md --platform-target 番茄小说
py -3 engine/novel_cli.py pipeline gate --phase 1
py -3 engine/novel_cli.py review --project ./novels/<slug>
py -3 engine/novel_cli.py export --format epub --project ./novels/<slug>
```

## Graphify

需 [graphify-novel](https://github.com/Anshler/graphify-novel) CLI；未安装时 bridge 降级 offline。

## 与 cursor-novel-video 衔接

章节 `chapters/*.md` → [cursor-novel-video](../cursor-novel-video/README.md)

## License

MIT
