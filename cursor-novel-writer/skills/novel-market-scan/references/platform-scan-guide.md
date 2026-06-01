# 平台扫榜指南（V1 — Agent 搜索版）

**不爬取、不绕过登录。** 通过联网搜索 + 公开页面 + 用户粘贴补充，生成结构化雷达。

## 目标平台（默认）

| 平台 | 搜索关键词示例 | 关注榜单/栏目 |
| --- | --- | --- |
| 番茄小说 | 番茄小说 榜 2026 | 新书榜、阅读榜、分类榜 |
| 起点中文网 | 起点 月票榜 畅销 | 畅销榜、三江、分类 TOP |
| 晋江文学城 | 晋江 金榜 言情 | 金榜、新文榜 |
| 知乎盐选 | 知乎盐选 短篇 热 | 盐选榜单、高赞短篇 |
| 抖音/快手推书 | 推书 爆款 类型 | 短视频带书常见类型（辅助） |

## Agent 执行步骤

1. 确认周期：**当周**（ISO 周）或 **当月**
2. 对每个平台执行 2–3 次定向搜索（含日期/「最新」）
3. 提取：**类型标签、高频设定、标题模式、开篇钩子类型**
4. 合并去重 → 输出 Top 10 题材簇（非单书名抄袭）
5. 对每个簇用 [short-video-fit-rubric.md](./short-video-fit-rubric.md) 粗评
6. 写入 `intel/radar/YYYY-Www.md`（模板见 [radar-report-template.md](./radar-report-template.md)）

## 数据质量

- 标注每条信息的 **来源 URL** 与 **检索日期**
- 无法验证的条目标 `(unverified)`
- 用户可粘贴榜单截图文字到对话，Agent 结构化入库

## 借鉴来源

- [oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode) `story-long-scan` / `story-short-scan`
- [InkOS Market Radar](https://github.com/Narcooo/inkos)
- [Manuscript](https://github.com/buildwithari/manuscript) 差异化评分思路
