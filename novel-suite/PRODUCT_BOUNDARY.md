# Novel Suite 产品边界

## 产品名

**Novel Suite**（工作名，正式商业化前需品牌/商标复核）

## 一句话定义

面向个人创作者与小型内容团队的小说创作与小说视频化工作流套件：选题 → 立项 → 写作 → 审稿 → 分镜 → 素材 → 发布前门禁。

## 三层能力分类

### 自有核心（可默认承诺）

- 统一项目结构与 SOP（`core/workflows/`）
- 中立数据契约（`core/contracts/`）
- 质量门禁（`core/gates/`）
- 自有 Prompt Pack（`prompt-packs/`）
- 资产注册与来源风险规则（`asset_registry` + `source_risk_gate`）
- 多 IDE 薄适配规则（`rules-packs/`）

### 可选适配器（默认关闭）

- TTS（`adapters/tts/`）
- 图像生成（`adapters/image-generation/`）
- 视频导出/合成（`adapters/video-export/`）
- 平台发布与采集（`adapters/platform-publishing/`）
- EPUB 导出（`ebooklib` — `pip install -e ".[epub]"`；禁入核心，见 `THIRD_PARTY_BOUNDARY.md`）

### 外部参考（不承诺、不复制原文）

- Anthropic/OpenAI/Vercel Skills 生态
- 外部开源小说/视频仓库
- `G:\SOLO小说项目`、`G:\Reasonix\SOLO小说视频项目` 历史素材（只读参考）

## 工程映射（非商业承诺）

| 产品层 | 工程候选 |
| --- | --- |
| Core workflows | `novel-suite writer` / Skills 对话流 |
| scene_to_video | `novel-suite video storyboard` + `storyboard.schema.json` |
| platform-publishing | `novel-suite auth` + `video publish`（需人工确认） |

工程能力在代码审查与许可证复核前，登记为**工程执行核心候选**，不写入商业卖点。

## 禁止表达

- 不把 Novel Suite 定义为「Cursor 专用插件」
- 不承诺默认全自动发布/采集
- 不把 AGPL/GPL 工具打包为默认内置
