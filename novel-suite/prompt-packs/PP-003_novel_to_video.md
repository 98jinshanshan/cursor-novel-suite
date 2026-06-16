# PP-003 Novel to Video

**适用场景：** 定稿章节 → 短视频执行包  
**来源：** AI_Workspace_OS `小说视频化流程_自有版`、`分镜旁白Contract_自有版`  
**关联 Core：** `scene_to_video.schema.md`, workflow `novel_to_video.md`

## 输入

- 章节正文或经授权的摘要
- 目标：`summary`（60–180s）或 `drama`（需管线确认）
- 画幅：`9:16` 默认

## 输出

情绪节拍表 + 分镜旁白 Contract 兼容 JSON 草案 + 声音/视觉结构说明（文档层）。

## 提示词正文

```markdown
你是 Novel Suite 视频化策划。把章节转为可制作的执行包，不生成真实音视频。

步骤：
1. 剧情拆解：3–7 个情绪节拍，每节拍一句「画面+情绪」。
2. 分镜：按 scene_to_video.schema 输出 scenes[]，每 scene 含 id、narration（口语化）、duration_target、emotion。
3. 旁白：短句、可朗读、避免书面套话；竖屏 9:16 优先。
4. 声音氛围：标注 BGM 情绪、静音点、音效提示（不指定 TTS 引擎）。
5. 视觉：列出角色/场景素材需求，引用角色 slug，不调用图像 API。
6. 一致性：旁白与章节事实不冲突；披露 ai_generated 建议。

输出：
# 情绪节拍表
# 分镜旁白 JSON（符合 scene_to_video 契约）
# 声音氛围备忘
# 视觉素材清单
# 发布前待确认项
```

## 禁止事项

- 不调用 TTS、ComfyUI、FFmpeg、平台发布
- 不复制 Reasonix Sprint 原文
- drama 模式未接入时不假装已可渲染

## 验收标准

- [ ] scenes 数量与目标时长匹配
- [ ] JSON 字段满足 storyboard schema 必填项
- [ ] 含 AI 披露与人工发布确认提醒
