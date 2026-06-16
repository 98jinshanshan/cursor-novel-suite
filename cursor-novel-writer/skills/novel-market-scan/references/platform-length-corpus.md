# 平台篇幅语料（Phase 0 L1）

> **主文档（必读）：** [PLATFORM-LENGTH-AND-NORMS.md](../../../../docs/standards/PLATFORM-LENGTH-AND-NORMS.md)
> — 含「4000 是否纯汉字」、分平台后台口径、引擎 CJK 约定。

## 一句话口径

| 概念 | 本项目引擎 | 平台后台 |
| --- | --- | --- |
| `words_per_chapter` | **章均汉字（CJK）** | 不一定；晋江/番茄常含标点 |
| 「日更 4000」 | 写入 `voice-brief` **日更汉字目标** | 起点/番茄指**每日更新总量** |

## 平台速查（章均 CJK 建议）

| platform_target | words_per_chapter | 日更（汉字） | 长篇章数 |
| --- | --- | --- | --- |
| 起点中文网 | 2800–4500（默认 3500） | 4000–6000 | 300+ |
| 晋江文学城 | 3000–4500（默认 3500） | 按全勤档 | 200+ |
| 番茄小说 | 2000–2500（默认 2200） | 4000–6000（后台计） | 100+ |
| 知乎盐选 | 单元 8000–25000 全稿 | 非日更连载 | 3–5 章/篇 |

## NEC

- **P0-S2** 补 radar「平台快照」时须增 **字数统计口径** 列  
- **P3** `novel audit plot` — [plot_scale_audit.py](../../../engine/scripts/plot_scale_audit.py)  
- **P5** `novel audit format` — [chapter_format_lint.py](../../../engine/scripts/chapter_format_lint.py)（CJK）

## 链接

- [platform-scan-guide.md](./platform-scan-guide.md)
- [platform-compliance.md](../../novel-review/references/platform-compliance.md)
