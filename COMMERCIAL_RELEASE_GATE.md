# Commercial Release Gate — Novel Suite

**状态：** 草案 / **待人工法律复核**  
**商业发布：** **不允许** — 待版权主体、第三方许可与用户最终确认后方可变更本文件结论。

本清单为商业发布前**门禁**（非自动 CI gate）。每项须人工勾选；Agent 不得将本文件解读为「已可对外销售」。

---

## 1. 产品核心

| # | 检查项 | 要求 | 状态 |
| --- | --- | --- | --- |
| 1 | 自有核心 | SOP、契约、门禁、Prompt/Rules Pack 为自有表达 | ☐ 待复核 |
| 2 | Prompt Pack | 不复制外部 Skill 原文 | ☐ 待复核 |
| 3 | Rules Pack | 仅薄适配，指向 `novel-suite/core/` | ☐ 待复核 |

## 2. 依赖与许可证

| # | 检查项 | 要求 | 状态 |
| --- | --- | --- | --- |
| 4 | `ebooklib` | 仅在 `pip install -e ".[epub]"` 或 legacy `cursor-novel-writer/requirements.txt`；**禁入** `[project] dependencies` 与 `dev` extra | ☐ B4 工程已拆分 |
| 5 | AGPL/GPL/NOASSERTION | 无默认 runtime 依赖含 SD WebUI、ControlNet、MediaCrawler | ☐ 待复核 |
| 6 | `jsonschema` | 允许为 MIT runtime 依赖 | ☐ 已满足 |
| 7 | `THIRD_PARTY_NOTICES.md` | 已更新并与 `THIRD_PARTY_POLICY.md` 一致 | ☐ B4 已更新 |

## 3. 适配器默认关闭

| # | 检查项 | 要求 | 状态 |
| --- | --- | --- | --- |
| 8 | TTS (`edge-tts`) | 默认关闭；用户自审 ToS | ☐ 待用户启用 |
| 9 | 图像生成 (SD/ControlNet/ComfyUI) | 默认关闭；用户自部署 | ☐ 待用户启用 |
| 10 | 视频导出 (FFmpeg) | 外部工具；用户自装 | ☐ 待用户启用 |
| 11 | 平台发布 / OAuth | 默认关闭；单次上传须**人工确认** | ☐ 待用户启用 |
| 12 | 平台采集 (MediaCrawler 等) | 商业版**禁用** | ☐ 待复核 |

## 4. 文档与误导风险

| # | 检查项 | 要求 | 状态 |
| --- | --- | --- | --- |
| 13 | README | 明示平台发布/TTS/图像/EPUB **默认关闭**与**人工确认** | ☐ B4 已强化 |
| 14 | `auth login` / `publish upload` | 示例命令旁有适配器警告 | ☐ B4 已强化 |
| 15 | `doctor --core-contracts` / `product validate` | 文档标明为只读/本地门禁，≠ 发布 | ☐ B4 已说明 |

## 5. 测试与工程验证

| # | 检查项 | 要求 | 状态 |
| --- | --- | --- | --- |
| 16 | `pytest -m "not ffmpeg"` | 全量回归通过（记录于 B4 执行报告） | ☐ 每次发布候选前重跑 |
| 17 | `novel-suite doctor --core-contracts --json` | `DOCTOR_CORE_OK` | ☐ 每次发布候选前重跑 |
| 18 | `novel-suite product validate --json` | `PRODUCT_VALIDATE_OK` | ☐ 每次发布候选前重跑 |
| 19 | `tests/test_commercial_compliance_gate.py` | 合规静态检查通过 | ☐ B4 已新增 |

## 6. 法律与发布决议

| # | 检查项 | 要求 | 状态 |
| --- | --- | --- | --- |
| 20 | 人工法律复核 | 律师或权利人书面确认 NOTICES/POLICY/LICENSE | ☐ **未完成** |
| 21 | 是否允许商业发布 | 须权利人签字后更新本节 | ☐ **不允许，待法律/用户最终确认** |

---

## 引用

- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
- [THIRD_PARTY_POLICY.md](THIRD_PARTY_POLICY.md)
- [novel-suite/THIRD_PARTY_BOUNDARY.md](novel-suite/THIRD_PARTY_BOUNDARY.md)
- [novel-suite/PRODUCT_BOUNDARY.md](novel-suite/PRODUCT_BOUNDARY.md)
- [docs/NOVEL_SUITE_B4_EXECUTION_REPORT.md](docs/NOVEL_SUITE_B4_EXECUTION_REPORT.md)
