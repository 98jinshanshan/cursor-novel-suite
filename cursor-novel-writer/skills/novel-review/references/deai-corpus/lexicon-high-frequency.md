# 高频 AI 味词汇（人类可读索引）

机器筛查使用 [lexicon.txt](./lexicon.txt)（**1100+** 条，由 `generate_deai_lexicon.py` 生成）。

## 分类

| 类 | 示例 | 严重度默认 |
| --- | --- | --- |
| 连接词堆叠 | 然而、此外、综上所述 | warn |
| 模板情绪 | 不禁、涌上心头、感到一阵 | warn |
| 模糊副词 | 仿佛、似乎、极其、十分 | nit |
| 综述体 | 值得注意的是、不难发现 | blocker |
| 网文滥觞 | 空气凝固、倒吸凉气 | warn |
| 装饰比喻 | 像一枚、像一滴、像一场、朱砂、白宣纸、未落的章 | warn |
| 喻体模板 | 睡着的案子、闭眼的监视器、小型火灾、未愈合的口子 | warn |

## 来源

- 仓库 [deai-checklist.md](../deai-checklist.md)、zencoder Sable、中文网文编辑惯例 `(curated)`
- 部分社区整理帖 `(unverified)` — 发书前以平台规则为准

## 维护

```bash
python cursor-novel-writer/engine/scripts/generate_deai_lexicon.py
```
