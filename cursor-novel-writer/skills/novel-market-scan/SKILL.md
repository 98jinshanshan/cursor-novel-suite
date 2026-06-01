---
name: novel-market-scan
description: |
  Weekly/monthly trending web-fiction topic radar for Chinese platforms, with short-video fit scoring.
  Use for 扫榜、题材雷达、热门题材、选题、market scan, 短视频选题, 番茄起点晋江榜单, Phase 0 选品.
license: MIT
compatibility: Requires monorepo root (intel/ directory). V1.1 adds CLI scan (`novel intel scan`) for cross-platform public-web trend collection.
metadata:
  author: cursor-novel-writer
  version: "1.0.0"
---

# Novel Market Scan（Phase 0 — P-1）

**上游选品 Skill**：在 `story-init` / `novel init` 之前，生成市场情报并驱动 `concept-brief` 立项。

工作区须为 **Novel Suite 根**（含 `.novel-suite-root`）。不确定时先运行 `novel suite doctor`。

## When to Use

- 写书前：当周/当月什么题材最火？
- 短视频推书：什么类型适合做成 summary/drama？
- 用户说：扫榜、选题、题材分析、market radar

## Outputs（固定路径）

| 产物 | 路径 |
| --- | --- |
| 周雷达报告 | `intel/radar/YYYY-Www.md` |
| 概念立项包（立项前） | `intel/concepts/<slug>.md` |
| 立项后副本 | `novels/<slug>/canon/concept-brief.md` |

## Workflow

1. 读 [platform-scan-guide.md](./references/platform-scan-guide.md) — 各平台搜索策略
2. 运行 CLI 扫描：

   ```bash
   python engine/novel_cli.py intel scan --period week
   ```

   - 自动跨平台检索公开网页热点（抖音/B站/快手/小红书/微博）
   - 写入 `intel/radar/YYYY-Www.md`
   - 生成 Top 候选 `intel/concepts/*.md`（可关闭）

3. 用户补充验证（必要时）→ 按 [radar-report-template.md](./references/radar-report-template.md) 修订报告
4. 对每个候选题材用 [short-video-fit-rubric.md](./references/short-video-fit-rubric.md) 评分
5. 推荐 Top 1–3；用户确认后：
   - 复制 [templates/concept-brief.md](../../templates/concept-brief.md) → `intel/concepts/<slug>.md`
   - 填表至 **approved**
6. 引导立项：

   ```bash
   python engine/novel_cli.py init --title "..." --premise "..." --concept ../../intel/concepts/<slug>.md
   python engine/novel_cli.py pipeline gate --phase 1 --project novels/<slug>
   ```

## Gate（与 novel-pipeline）

- **无** `canon/concept-brief.md` → 禁止进入 Phase 1 实质写作（世界观/章节）
- `task_plan.md` Phase 0 须 `[x]`（`init --concept` 自动勾选）

## CLI 辅助

```bash
python engine/novel_cli.py intel paths          # 打印 intel/ 与当周 radar 路径
python engine/novel_cli.py intel scan --period week
python engine/novel_cli.py intel scan --period month --no-concepts
python engine/novel_cli.py intel scan --demo --period week   # 离线 smoke（非 live 数据）
python engine/novel_cli.py pipeline gate --phase 1
```

## 工业闭环（远期 P-1e）

上传/播放数据 → 下一周 radar 权重调整（V2+；当前 V1 仅搜索报告）。

## References

- [Platform scan guide](./references/platform-scan-guide.md)
- [Short-video fit rubric](./references/short-video-fit-rubric.md)
- [Radar report template](./references/radar-report-template.md)
- [novel-pipeline Phase 0](../novel-pipeline/SKILL.md)

Do **not** scrape logged-in pages or violate platform ToS. CLI 仅检索公开网页结果，不登录平台账号。
