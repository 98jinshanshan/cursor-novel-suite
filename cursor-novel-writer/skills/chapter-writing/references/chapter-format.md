# 章节 Markdown 格式规范

> **读者：** chapter-writing、novel-review、SOLO/TRAE Agent。  
> **默认：** `chapter_structure: continuous` — **单章内禁止「一、二、三」式小节**（含 `## 一` 与单独一行 `一`）。

## 1. 禁止章内「一、二、三」（Blocker）

| 禁止写法 | 说明 |
| --- | --- |
| 单独一行 `一` / `二` / `三` | 旧 Agent 易犯；一律删除，改为段落换行 |
| `## 一` / `## 二` / `## 三` | 章内小节标题；**不得出现** |
| `一、` `二、` `三、` 作段首标记 | 视同小节，禁止 |

**允许：** 场景切换只用**空行**；必要时章内仅用 `---`（慎用，一章 ≤1 次）。  
**叙事连贯：** 起承转写在段落里完成，不靠小标题切章。

仅当 `voice-brief.md` 显式写 `chapter_structure: scene-beats` 且用户确认时，才可恢复 `## 一/二/三`（侯府春深等默认书 **不要** 用）。

## 2. 标准模板（默认 `continuous`）

```markdown
# 第N章：章节标题

---

[连贯正文：段落之间空行分隔，无「一/二/三」小节]

---

（第N章完）
```

**硬性要求（novel-review Blocker）：**

- [ ] 首行 `# 第N章：标题` 与 `chapters/NN_标题.md` 一致
- [ ] 章首、章尾各一行 `---`
- [ ] 章尾 `（第N章完）`
- [ ] 全文**无** §1 禁止的「一、二、三」小节
- [ ] 目标字数 3500–5500（或 `project.json` / 用户约定）

## 3. `voice-brief.md` 必填项

```markdown
| chapter_structure | continuous |
```

写章前 Agent **必须 Read** `canon/voice-brief.md`；若为 `continuous` 却写出 `## 一` → **Format blocker**。

## 4. 旧稿迁移（已有 ## 一/二/三）

1. 保留 `# 第N章`、`---`、`（第N章完）`
2. 删除所有 `## 一/二/三` 及单独一行「一」「二」「三」
3. 删标题后**不要删剧情**，用空行衔接段落
4. 写 `reviews/chNN-review.md` 的 Format 记「已去章内小节」

## 5. 与 EPUB / 视频

- EPUB：仅 `# 第N章` 进目录；无章内 ## 小节，版式更干净
- 视频分镜：按段落或 Agent 手拆，**不**依赖 `## 一`

## 6. 验收

```bash
python engine/novel_cli.py review --chapter chapters/NN_*.md --project novels/<slug>
```

审稿 **## Format** 须含：`chapter_structure=continuous`，且无章内一二三。
