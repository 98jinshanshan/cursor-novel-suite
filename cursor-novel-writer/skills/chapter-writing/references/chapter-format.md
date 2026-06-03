# 章节 Markdown 格式规范

> **读者：** chapter-writing、novel-review、SOLO/TRAE Agent。  
> **目的：** 统一落盘格式，避免「只有正文、无结构」或「一二三」与网文常见分节混淆。

## 1. 「一、二、三」是什么？是不是写作事故？

**不是事故。** 本工具链将 **一章内的三个场景节拍** 标为 `## 一` / `## 二` / `## 三`，对应短篇内的 **起—承—转**（见 chapter-writing SKILL「Chapter Structure」）。

| 含义 | 说明 |
| --- | --- |
| 不是卷/部/篇编号 | 全书仍用 `chapters/01_标题.md`、`02_标题.md` |
| 不是番茄/起点常见的「第1节」 | 平台章内小标题若另有要求，在 `voice-brief.md` 的 `chapter_structure` 覆盖 |
| 必须写成 Markdown 二级标题 | `## 一`，**禁止**仅单独一行纯文字 `一`（无 `#`） |

若 `voice-brief.md` 设定 `chapter_structure: continuous`（连续叙事、无节拍标题），则**不要**使用 `## 一/二/三`，改用场景空行或 `---` 分隔（见 §3）。

## 2. 标准模板（默认 `scene-beats`，网文/古言通用）

```markdown
# 第N章：章节标题

---

## 一

[场景 1：时间地点 + 入场动作]

## 二

[场景 2：冲突 / 对话 / 信息推进]

## 三

[场景 3：转折 + 章末钩子]

---

（第N章完）
```

**硬性要求（novel-review Blocker）：**

- [ ] 文件首行 `# 第N章：标题` 与文件名 `NN_标题.md` 一致
- [ ] 章首、章尾各有一行 `---`
- [ ] 三个节拍均为 `## 一` / `## 二` / `## 三`（全角数字，无顿号）
- [ ] 章尾有 `（第N章完）`
- [ ] 目标字数 3500–5500（除非 `project.json` 或用户另有约定）

## 3. 可选结构（须在 voice-brief 写明）

| `chapter_structure` | 用法 |
| --- | --- |
| `scene-beats`（默认） | §2 模板 |
| `continuous` | 无 `## 一/二/三`；场景之间用空行 + 可选 `---` |
| `platform-sections` | 按 `platform_target` 用小节标题（如「1」「2」或平台编辑要求），仍须保留 `# 第N章` 与 `（第N章完）` |

## 4. 常见 Agent 失误（须修后再 promote）

| 现象 | 判定 | 修复 |
| --- | --- | --- |
| 正文以 `第1章：入府` 开头但无 `#` | 格式 blocker | 补 `#` |
| 单独一行 `一` / `二` / `三` | 格式 blocker | 改为 `## 一` 等 |
| 缺少 `（第N章完）` | 格式 blocker | 章尾补上 |
| 只有一章正文、无场景切分且超 6000 字 | warn | 考虑拆章或加 `## 二/三` |
| 节拍仅 2 个却标三章 | warn | 合并节拍或补第三场景 |

## 5. 与 EPUB / 视频导出

- `novel export` / EPUB：依赖 `#` / `##` 生成目录层级；纯文本 `一` 会被当正文，**目录错乱**。
- `video-chapter-summary`：分镜常按 `##` 切场景；无标题则整章单镜头。

## 6. 验收命令

```bash
# 人工或 Agent 写完后
python engine/novel_cli.py review --chapter chapters/NN_*.md --project novels/<slug>
```

审稿报告须含 **## Format** 小节（见 novel-review forge 阶段 1）。
