# Skills 安装规范（canonical）

**版本：** 1.0（2026-06-02）  
**权威安装方式：** 仓库根 `platforms/install-skills.ps1`（或 `npx skills add`）  
**不要用：** 手抄 `SKILL.md`、`skills-lock.json`（已 gitignore，仅本地 npx 产物）

---

## Phase 0 命名对照（重要）

| 用户说法 | 实际 Skill 目录 | 说明 |
| --- | --- | --- |
| Phase 0 / 扫榜 / 选题 | **`novel-market-scan`** | 无 `phase-0/` 目录 |
| 全流程总控 | **`novel-pipeline`** | Phase 0 委托给 `novel-market-scan` |
| 立项 | `story-init` | 前置：Phase 0 gate 通过 |

Agent **必须先 Read** `novel-market-scan/SKILL.md`，再跑 `novel intel scan`。

---

## 完整 Skill 清单（13）

### 小说（10）— `cursor-novel-writer/skills/`

| Skill | Phase / 用途 |
| --- | --- |
| **`novel-market-scan`** | **Phase 0 选品** |
| **`novel-pipeline`** | **总控 Phase 0–9** |
| `story-init` | Phase 1 立项 |
| `worldbuilding` | Phase 2 |
| `character-management` | Phase 2 |
| `plot-structure` | Phase 3 |
| `chapter-writing` | Phase 5 |
| `novel-review` | Phase 6–8 |
| `novel-export` | Phase 9 |
| `novel-marketing` | 可选营销 |

### 视频（3）— `cursor-novel-video/skills/`

| Skill | 用途 |
| --- | --- |
| `video-chapter-summary` | 章节摘要短视频 |
| `video-scene-drama` | 分场景叙事 |
| `video-export` | 多尺寸 / QC |

---

## 安装命令

```powershell
# 全平台（在 Novel Suite 根）
powershell -File platforms/install-skills.ps1

# 仅 TRAE / SOLO
powershell -File platforms/install-skills.ps1 -Agents trae-cn
```

---

## 已克隆项目补丁更新

```powershell
powershell -File platforms/patch-update.ps1 -Agents trae-cn
```

详见 [solo-clone-checklist.md](../verification/solo-clone-checklist.md)。

---

## 验证

```powershell
py -3 cursor-novel-writer/engine/novel_cli.py suite doctor
Test-Path .trae\skills\novel-market-scan\scripts\intel_scan.py
py -3 cursor-novel-writer/engine/novel_cli.py intel paths
```

`suite doctor` 中 `writer_skills_source` 应为 **10**，`skills_trae-cn_*` 应为 **13**（含 video）。
