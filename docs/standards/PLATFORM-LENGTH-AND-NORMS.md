# 各平台篇幅与字数规范（2026-06-04 修订）

> **用途：** Phase 0 选平台、Phase 3 大纲、`story.md` / `voice-brief.md` 字数契约、`chapter_format_lint` / `plot_scale_audit`。  
> **非法律意见：** 签约、全勤、发文额度以各平台**作家后台最新公告**为准；本文标注来源等级。

| 标注 | 含义 |
| --- | --- |
| `official` | 平台作家专区/规则公告原文或明确条款 |
| `community` | 编辑口径、问答、行业文章，需发书前再核对 |
| `engine` | 本仓库 **Novel Suite 引擎** 自定口径（与各平台后台可能不一致） |

**相关文档：** [AUDIT-REFERENCES-INDEX.md](./AUDIT-REFERENCES-INDEX.md) ·
[platform-length-corpus.md](../../cursor-novel-writer/skills/novel-market-scan/references/platform-length-corpus.md)

---

## 0. 先回答：「4000 字」是纯汉字吗？

### 0.1 在本项目里（写作 / lint / `story.md`）

| 字段 / 工具 | 统计口径 | 是否含标点/空格/标题 |
| --- | --- | --- |
| `words_per_chapter`（`story.md` front matter） | **目标：章均汉字数** | 约定为 **CJK 汉字** `[一-龥]` |
| `chapter_format_lint` → `count_cjk()` | **正文文件内汉字个数** | **不含**标点、英文、数字、空格、`# 标题`、`---`、`（第N章完）` |
| `plot_scale_audit` | 对照 `words_per_chapter` 与平台表 | 同上语义 |

**结论：** 技能里写的「3500–5500 字/章」在未特别声明时，指 **汉字字数（CJK）**，不是各平台后台的「计费字数」。

### 0.2 在各平台后台（发表 / 全勤 / 日更打卡）

各站**不一致**，且常与 Word「字符数」不同：

| 平台 | 后台一般怎么计 | 与引擎 CJK 差 |
| --- | --- | --- |
| **番茄** | 章节**正文**（不含标题）；日更额度含**当日新章 + 修改增量** | 通常 **多于** CJK（含标点） |
| **晋江** | **汉字 + 标点 + 空格**（网友实测 Word 少 5%–15%） | **多于** CJK |
| **起点** | 作家助手/订阅按章展示；日更 4000 指**更新量**非单章上限 | 单章无统一「纯汉字」公示 |
| **盐选** | 投稿按**全稿**；回答引流 3000–5000 为试读段 | 与连载章计不同 |

**切勿混用：**

- ❌ 「起点日更 4000」≠「每一章必须写 4000 汉字」
- ❌ 「晋江全勤每日 3000」≠「CJK 3000」（后台字数往往更高）
- ❌ Word 字符数 ≠ 番茄后台字数 ≠ 本仓库 `count_cjk`

---

## 1. 分平台对照表（2026-06 检索）

### 1.1 起点中文网 / 阅文男频（你当前 `冷案回声`）

| 维度 | 规则摘要 | 来源 |
| --- | --- | --- |
| **单章字数（创作建议）** | 男频常见 **2000–4000**；社区黄金 **2500–3500**；也有 **3000–8000** 区间说法 | `community` [起点问答](https://m.qidian.com/ask/qqboszfvxycnj) |
| **日更 4000+** | 指 **每日更新字数合计**（维持推荐/全勤习惯），**不是**单章下限 | `community` 编辑方法论转载 |
| **签约门槛** | 正文满 **6000** 可进初审；**3 万** 字前后受编辑关注 | `community` |
| **长篇体量** | 连载 **100 万–500 万+**；冲榜常 **200 万+ / 500 章+** | `community` |
| **本项目建议** | `words_per_chapter: 3500`（CJK）；`target_chapters: 200–500`；日更目标 **4000–6000 汉字/日**（可 1–2 章） | `engine` |

### 1.2 番茄小说

| 维度 | 规则摘要 | 来源 |
| --- | --- | --- |
| **单章** | 推书/教程常写 **2000 字/章** 利于节奏；与「日更 4000」配合可 **一天 2 章** | `community` |
| **日更全勤** | **有效更新 ≥4000 字/自然日**（进阶 **6000**）；满 **10 万** 字次月起；听读收益门槛等见福利页 | `official` [全勤规则变更公告](https://fanqienovel.com/writer/zone/article/7295651439395733530)、`community` [2025 福利说明](https://fanqienovel.com/writer/zone/article/7444811345830101017) |
| **日更额度口径** | **章节正文字数（不含标题）**；修改旧章只计**增量**；删章/审核失败返还额度 | `official` [长篇发文规则第二版](https://wangwen666.com/post/189.html) 转载平台 2026-05-22 条款 `community` |
| **本书引擎** | `words_per_chapter: 2200–2500`（CJK）；勿用 4000 当「章均」 | `engine` |

### 1.3 晋江文学城

| 维度 | 规则摘要 | 来源 |
| --- | --- | --- |
| **短篇入库** | 完结 **≤10 万字** 按短篇；**10 万+** 为常规长篇语境 | `community` |
| **章均** | 常见 **2500–5000**（含标点后台计）；Word **2900 → 后台约 3000** 经验比例 | `community` [bbs 字数统计](https://bbs.jjwxc.net/showmsg.php?board=17&id=452224) |
| **VIP 全勤** | 自然月 **每日** VIP 章更新达 **3000 / 6000 / 9000**（**含标点、空格**）；月累计含罚额 **10 万 / 20 万 / 30 万** | `official` [全勤说明](http://www.jjwxc.net/sp/indexAd/index.html) |
| **本书引擎** | `words_per_chapter: 3500–4500`（CJK，约等于后台 3800–5000） | `engine` |

### 1.4 知乎盐选

| 维度 | 规则摘要 | 来源 |
| --- | --- | --- |
| **短篇投稿** | 完稿 **≥8000**（官方小助手写 **故事类 ≥5k**）；常见过稿 **1–2.5 万** | `official` [盐选 FAQ](http://s.zhihu.com/CvhTM) `community` |
| **结构** | **3–5 章**；免费段 **2000–5000** 须出核心冲突 | `community` |
| **连载长篇** | 大纲 + 样章 **3–5 万**；全书常 **10–30 万** | `community` |
| **本书引擎** | 不按章连载；走 `plot/chapter-plan` 短篇单元即可 | `engine` |

---

## 2. 引擎默认契约（`plot_scale_audit` / 模板）

`engine/scripts/plot_scale_audit.py` → `PLATFORM_DEFAULTS`：

| platform_target | target_chapters 参考 | words_per_chapter（**CJK**） | 日更汉字参考（非 story 字段） |
| --- | --- | --- | --- |
| 起点中文网 | 300–1500 | **3500**（允许 2800–4500） | **4000–6000/日** |
| 晋江文学城 | 200–500 | **3500**（允许 3000–4500） | 按全勤档折算 |
| 番茄小说 | 100–800 | **2200**（勿 >3500） | **4000–6000/日**（后台计） |
| 通用 | 12–999 | 4000 | — |

`chapter_format_lint` 默认 band：`words_per_chapter × 0.7` ~ `× 1.5`（CJK）。

---

## 3. 常见误区（本次修订针对）

| 误区 | 正确理解 |
| --- | --- |
| 全书 `words_per_chapter: 4000` = 平台「日更 4000」 | 前者是**章均汉字目标**；后者是**每日更新总量**（番茄/起点运营） |
| 技能默认 4000 = 各站统一标准 | 只有 **engine 模板默认值**；番茄章均应 **下调** |
| lint 字数 = 后台全勤字数 | lint 用 **CJK**；晋江/番茄后台常 **大于** CJK |
| 12 章大纲 × 4000 = 百万字长篇 | 12 应是 **节拍**；正文章数 = `target_chapters`（如 300） |

---

## 4. 立项时必须写的字段

在 `story.md` + `canon/voice-brief.md` 中显式写明：

```yaml
# story.md（示例：起点悬疑）
platform_target: 起点中文网   # 在 voice-brief 表内
target_chapters: 300
words_per_chapter: 3500      # 章均 CJK 汉字，非平台后台字数
daily_update_cjk: 4500       # 建议新增到 voice-brief「连载节奏」段（汉字/日）
```

发章前用后台预览核对：若晋江/番茄后台比 CJK 少 **300–800**，属正常，写作时按上表 **上浮目标**。

---

## 5. 仓库内文档索引

| 文档 | 路径 |
| --- | --- |
| 章节格式 + 字数 band | [chapter-format.md](../../cursor-novel-writer/skills/chapter-writing/references/chapter-format.md) |
| 排版 | [chinese-prose-layout.md](../../cursor-novel-writer/skills/chapter-writing/references/chinese-prose-layout.md) |
| chapter-writing Skill | [SKILL.md](../../cursor-novel-writer/skills/chapter-writing/SKILL.md) |
| 文风模板 | [voice-brief.md](../../cursor-novel-writer/templates/voice-brief.md) |
| 扫榜语料入口 | [platform-length-corpus.md](../../cursor-novel-writer/skills/novel-market-scan/references/platform-length-corpus.md) |
| P3 校验 | `novel audit plot` → `plot_scale_audit.py` |
| P5 校验 | `novel audit format` → `chapter_format_lint.py`（**CJK**） |

---

## 6. Phase 0 检索记录（2026-06-04）

- 番茄：全勤 4000/6000、发文额度、正文不含标题 — 作家专区公告 + 2026 发文规则转载  
- 起点：章均 2000–4000、日更 4000 为更新习惯 — 问答/社区  
- 晋江：全勤 3000/6000/9000 含标点空格 — 官网全勤页 + bbs  
- 盐选：短篇 8k+ 完稿 — 盐选作者 FAQ + 社区  

---

*下次扫榜时 Agent 应更新 §1 表格「来源」列并刷新 `intel/radar` 平台快照中的「字数口径」行。*
