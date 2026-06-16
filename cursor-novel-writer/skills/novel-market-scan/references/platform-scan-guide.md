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

## 与 CLI 分工（NEC P0-S1 / P0-S2）

| 平台类型 | 子任务 | 执行体 |
| --- | --- | --- |
| 抖音/B站/快手/小红书/微博 | P0-S1 | `novel intel scan`（`intel_scan.py`） |
| 番茄/起点/晋江/盐选 | P0-S2 | **Agent** 按本指南搜索，填入 radar `## 平台快照` |

CLI 扫描后 radar 已含「平台快照」骨架表；Agent **必须**替换 `(待补全)` 行并标注来源与 `(unverified)`。

## Agent 执行步骤（P0-S2）

1. 确认周期：**当周**（ISO 周）或 **当月**（与 `intel paths` 一致）
2. 对 **文字平台** 各执行 2–3 次定向搜索（含日期/「最新」）
3. 提取：**类型标签、高频设定、标题模式、开篇钩子类型**
4. 合并去重 → 补全 Top 10 题材簇（与 CLI 热度榜对照）
5. 对每个簇用 [short-video-fit-rubric.md](./short-video-fit-rubric.md) 粗评
6. 各平台表增加 **字数统计口径** 行（CJK / 含标点 / 日更额度）— 见
[PLATFORM-LENGTH-AND-NORMS.md](../../../../docs/standards/PLATFORM-LENGTH-AND-NORMS.md)
7. 更新 `intel/radar/YYYY-Www.md` 并刷新 `*.completion.json` 中 P0-S2/P0-S3 为 `done`

## 离线 / 联网失败（P0-S1 降级）

CLI 直连检索失败或零命中时，**禁止**跳过 Phase 0：

1. `novel intel scan --period week --fallback-demo`（零命中自动加载 `intel/fixtures/smoke-hits.json`）
2. 仍失败 → `--demo` 或 `--input <自采 hits.json>`
3. 必须执行本指南 **P0-S2** 补全文字平台 `## 平台快照`（fixture 不含番茄/起点真实榜）
4. 周报复用 [radar-report-template.md](./radar-report-template.md) 或复制上周 radar 骨架，只更新摘要与表格

## 数据质量

- 标注每条信息的 **来源 URL** 与 **检索日期**
- 无法验证的条目标 `(unverified)`
- 用户可粘贴榜单截图文字到对话，Agent 结构化入库

## 借鉴来源

- [oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode) `story-long-scan` / `story-short-scan`
- [InkOS Market Radar](https://github.com/Narcooo/inkos)
- [Manuscript](https://github.com/buildwithari/manuscript) 差异化评分思路
