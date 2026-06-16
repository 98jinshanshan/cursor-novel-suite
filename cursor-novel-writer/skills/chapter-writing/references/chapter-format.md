# 章节 Markdown 格式规范

> **读者：** chapter-writing、novel-review、SOLO/TRAE Agent。  
> **叙事排版（段首缩进、对话引号）：** 必读 [chinese-prose-layout.md](./chinese-prose-layout.md)  
> **默认：** `continuous` — 单章内禁止「一、二、三」小节。

## 1. 禁止章内「一、二、三」（Blocker）

| 禁止写法 | 说明 |
| --- | --- |
| 单独一行 `一` / `二` / `三` | 删除，改为空行 + 缩进段落 |
| `## 一` / `## 二` / `## 三` | 章内小节标题，不得出现 |

## 2. 标准模板（文件层 + 叙事层）

```markdown
# 第N章：章节标题

---

　　[第一段：必须以两个全角空格开头]

　　[第二段……]

　　“对话也独立成段，”她说，“段首同样缩进。”

---

（第N章完）
```

**硬性要求：**

- [ ] `# 第N章` 与文件名一致；首尾 `---`；`（第N章完）`
- [ ] 叙事层段首 `　　`（见 chinese-prose-layout.md）
- [ ] 无章内一二三；无顶格正文块
- [ ] 章均 **汉字（CJK）** 字数：读 `story.md` → `words_per_chapter`（默认 band 0.7–1.5×）；**不是**平台后台「含标点」字数 — 见
[PLATFORM-LENGTH-AND-NORMS.md](../../../../docs/standards/PLATFORM-LENGTH-AND-NORMS.md)
- [ ] 装饰比喻：同章少用「像一枚/像一滴/朱砂」；替换表见
[narrative-patterns.md](../../novel-review/references/deai-corpus/narrative-patterns.md) §装饰比喻

## 3. `voice-brief.md`

| 字段 | 默认 |
| --- | --- |
| `chapter_structure` | `continuous` |
| `prose_layout` | `cn-fiction-indent` |

## 4. 旧稿迁移

1. 去章内 `一/二/三` / `## 一`
2. 为正文补 `　　` 段首缩进
3. 对话改 `“”`，独立成段

## 5. 验收

```bash
python engine/novel_cli.py review --chapter chapters/NN_*.md --project novels/<slug>
```

**## Format** 须含：`prose_layout=cn-fiction-indent`，段首缩进 ✅。
