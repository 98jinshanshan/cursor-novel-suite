# 中文小说去 AI 味清单

> 阶段 7（Sable pass）必查。来源：zencoder Sable copy edit + postwriter soft critics + 中文网文编辑惯例。  
> **章节 Markdown 格式（`# 第N章`、`## 一/二/三`）在 Phase 6 硬校验，不在本表重复。**

## A. 句式与连接词

- [ ] 段首连续「然而 / 但 / 不过 / 与此同时」≤ 1 次/千字
- [ ] 无「不禁 / 忍不住 / 不由得」堆叠（同章 ≤ 2 次）
- [ ] 无「仿佛 / 好像 / 似乎」三连在同一小段
- [ ] 无翻译腔：「他感到一阵 X 涌上心头」类模板句

## B. 说明 vs 呈现

- [ ] 对话无「正如你所知」式信息_dump
- [ ] 情绪通过动作/细节呈现，非形容词直述（少「非常 / 十分 / 极其」）
- [ ] 章末无总结式说教或点题段（除非 voice-brief 允许）

## C. 重复与密度

- [ ] 同场景「目光 / 眼神 / 视线」≤ 2 次
- [ ] 无连续 3 句以上排比
- [ ] 无 AI 高频词：「深入探讨」「值得注意的是」「总的来说」

## D. 对话自然度（Fiction Workshop Reader Test 简化）

- [ ] 朗读对话：是否像真人说话（可删 10% 而不丢信息）
- [ ] 人物说话方式与 `characters/*.md` 一致

## E. 对照 voice-brief

- [ ] 句长、人称、禁用词与 `canon/voice-brief.md` 一致

## F. 平台合规（platform_target）

对照 [platform-compliance.md](./platform-compliance.md) 与 `canon/project.json` → `platform_target`：

- [ ] 未触犯该平台 AI 正文红线
- [ ] 无批量模板化、可互换段落到任意章节
- [ ] 细节与本书设定绑定（非通用 AI 例句）

## 输出

在 `reviews/chNN-review.md` 增加 **De-AI** 小节，每项标 ✅ / ❌；任一 ❌ 不得进入 Phase 9 导出。
