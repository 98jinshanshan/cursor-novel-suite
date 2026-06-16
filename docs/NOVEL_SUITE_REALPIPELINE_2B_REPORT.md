# Novel Suite RealPipeline-2B 执行报告

**日期：** 2026-06-15  
**项目：** `novels/novel-837dd4f1`（冷案回声）  
**制度：** NVP — Execute → Verify Prompt → Evidence → Verdict → Handoff

---

## 背景

RealGen-1 被正式废止（D 级）。RealPipeline-2B 在 **active novel** 内重建证据链，覆盖 Phase 0–9 与视频 V1D/V2。

---

## 制度文件

| 路径 | 状态 |
| --- | --- |
| `docs/standards/NODE-VERIFICATION-PROMPT-CONTRACT.md` | ✅ |
| `docs/verification-prompts/NVP-*.md` ×15 | ✅ |
| `cursor-novel-writer/skills/voice-brief/` | ✅ |
| `cursor-novel-video/skills/video-motion-drama/references/node-dispatch.md` | ✅ |

---

## 小说链（Phase 0–9）

| 节点 | 证据 | Verdict |
| --- | --- | --- |
| Isolation | `reports/realpipeline_2b_active_project_isolation.md` | pass |
| P0 | `reports/phase0_source_record.md` | pass（live scan blocked，有 radar 来源） |
| P1–P4 | canon / plot / voice-brief 沿用 | pass |
| P5 | `chapters/02_双签.md` · **3301 CJK** | pass |
| P6 | `reviews/02_双签-review.md` | pass |
| P7 | `reviews/02_双签-deai.md` + platform-compliance | pass |
| P8 | `canon/snapshots/ch02-after.md` | pass |
| P9 | export | **fail**（commercial blocked） |

角色 canon：**林骁、陈琪、傅正昆、苏晚晴**（非 RealGen 林澄/程砚）。

---

## 视频链（V1D / V2）

| 节点 | 证据 | Verdict |
| --- | --- | --- |
| V1D | `video/ch02/storyboard.json` 等工程包 | **fail · grade C** |
| V2 | `video/ch02/video_qc_report.md` | **fail · video_level: C** |

**原因：** 无 ch02 渲染 MP4；ComfyUI/TTS 未执行；动态文字卡不得评 A/B。

---

## 总评级（最短板）

```text
overall_grade: C
weakest_link: video
```

小说 Phase 0–8 证据齐全；视频与 P9 export 为短板。**不得**宣称 AI 短剧成片完成。

---

## CLI / 测试

```powershell
novel_suite.cli realpipeline validate --project novels/novel-837dd4f1 --json  # OK
pytest tests/test_realpipeline_2b.py -q  # 11 passed
```

`realgen-demo run` → `REALGEN_DEMO_DEPRECATED`。

---

## 边界

`commercial_release_allowed=false` · `verdict=blocked` · 未读 SOLO/Reasonix · 未联网 API

---

## 下一步（Handoff）

1. 跑 ComfyUI + TTS 完成 ch02 motion-drama 真渲染
2. 更新 `video_qc_report.md` 至 A/B 后重跑 V2
3. commercial gate 打开后再 P9 export
