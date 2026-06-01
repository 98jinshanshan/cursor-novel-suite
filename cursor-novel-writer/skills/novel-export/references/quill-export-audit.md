# Quill 出版输出 Audit（ZE-08）

导出 EPUB 前按 zencoder **Quill** 角色执行最后一轮出版检查。任一 ❌ 应修复后再 `novel export`。

## 文稿完整性

- [ ] `chapters/_index.md` 与 `chapters/*.md` 文件名、顺序一致
- [ ] 无空章、无占位标题（「待写」「TBD」）
- [ ] `story.md` 含书名、作者（或 canon/project.json 已填 author）

## 结构与元数据

- [ ] `canon/project.json`：`title`、`slug`、`platform_target` 正确
- [ ] 各章 frontmatter（若有）与正文标题不冲突
- [ ] `canon/progress.json` 字数/章数与实稿大致吻合

## 合规与质量（Gate）

- [ ] Phase 6–8 已完成：`reviews/` 最新章无 open blocker
- [ ] De-AI + [platform-compliance.md](../../novel-review/references/platform-compliance.md) 全绿
- [ ] `canon/voice-brief.md` 禁词/风格在终稿中已落实

## EPUB 技术

- [ ] `pip install ebooklib` 可用
- [ ] 试运行：`novel export --format epub --output dist/书名.epub`
- [ ] 打开 EPUB：目录可点、中文缩进/行距正常、无乱码

## 可选（平台投稿）

- [ ] 营销：`novel-marketing` 标题/简介（用户要求时）
- [ ] 平台字数/章节规范（对照 platform_target）

## 失败处理

| 问题 | 动作 |
| --- | --- |
| 缺章 | 回 Phase 5 `chapter-writing` |
| blocker 未关 | 回 Phase 6 + repair spec |
| de-AI ❌ | 回 Phase 7 |
| EPUB 构建失败 | 查 create_epub.py stderr，修 frontmatter/路径 |
