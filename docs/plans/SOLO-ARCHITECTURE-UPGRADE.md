# SOLO 专家团架构升级计划

> **来源**：`G:\Reasonix\SOLO小说视频项目` 五份规划文档 + DeepSeek 专家团纪要  
> **基线**：CURSOR 审计 37/100（2026-06-06）；视频侧已演进至 Wan/ComfyUI + Brain QC  
> **目标**：12 周内 37 → 75 分；**Python 增量嫁接**，不重写 JS/TS  
> **协作协议**：[FICUS 增量交付规则](../../.cursor/rules/ficus-incremental-delivery.mdc)

---

## 1. 架构诊断

```text
成熟区（保留）                    空白区（增量填充）
─────────────────                ─────────────────
intel / init / chapter           memory（向量记忆）← Sprint 1 已启动
gate / registry / result         publish 自动化
export / Skills 多 IDE           analytics 反馈闭环
cursor-novel-video               REST API（Phase 2）
  Brain / Still / Motion 节点
```

**技术路线**：保留 ComfyUI + Wan 2.1 视频主线；SOLO 原 SD WebUI MVP 仅作 summary 回退。

---

## 2. 代码边界（强制）

| 可改 | 禁碰（除非架构评审） |
| --- | --- |
| `src/novel_suite/memory/*` | `writer/gate.py` |
| `cursor-novel-video/engine/*` | `core/result.py` |
| `cursor-novel-video/adapters/*` | `core/errors.py`（仅追加错误码） |
| `tests/memory/*` | `writer/registry.py` |
| `skills/*/references/*` | 单 PR >5 个文件 |

**禁止**：同一 PR 同时改小说侧与视频侧。

---

## 3. 六 Sprint 路线图

| Sprint | 周期 | 目标 | 状态 |
| --- | --- | --- | --- |
| **S0** 基础加固 | 1 周 | 文档 D P0：凭据、端口、FFmpeg、Prompt 防护 | **✅ 已完成** |
| **S1** 向量记忆 | 2 周 | Qdrant/M3E + 四层存储 + 双轨 recall | **S1.2 Qdrant 混合检索 + sync/probe 已落地** |
| **S2** 视频 MVP | 3 周 | Wan T2V ref 全量、Brain QC 闭环、53 镜 E2E | 部分已有 |
| **S3** 多平台发布 | 2 周 | Playwright 上传 + 发布归档 | 未开始 |
| **S4** 质量自动化 | 2 周 | 向量一致性 + 自动角色卡 + 文风 | 未开始 |
| **S5** 数据飞轮 | 2 周 | 看板 + 创作建议（可后置） | 未开始 |

---

## 4. Sprint 1 — 向量记忆（节点 3）

### 4.1 四层模型

| 层 | 用途 | 示例 |
| --- | --- | --- |
| **L1** | 宏观摘要 | 全书梗概、主线弧 |
| **L2** | 中观章节 | 章摘要、关键事件 |
| **L3** | 微观场景 | 单场戏、对白片段 |
| **L4** | 设定 | 角色外貌、世界观规则 |

### 4.2 存储策略

1. **默认**：`novels/<slug>/canon/memory/{layer}.jsonl`（CI 友好，零依赖）
2. **索引**：`QDRANT_URL` + `qdrant-client` → `memory sync` 批量同步；检索 Qdrant 优先、JSONL 回退

### 4.3 双轨接口

| 函数 | 用途 |
| --- | --- |
| `recall_for_writing` | 写作时召回 L2/L4 |
| `recall_for_video` | 视频时召回 L3/L4 + CVDP 标签 |
| `check_consistency` | 新文本 vs 已有 L4 设定对比 |

### 4.4 CLI

```powershell
novel-suite memory store --text "..." --layer L4 --tags "character,林墨" --project novels/<slug> --json
novel-suite memory search --query "林墨眼睛" --layer L4 --project novels/<slug> --json
novel-suite memory check --text "林墨蓝眼睛" --project novels/<slug> --json
novel-suite memory probe --project novels/<slug> --json
novel-suite memory sync --project novels/<slug> --reembed --json
```

部署：`platforms/install-memory-stack.ps1`；验证：[memory-qdrant.md](../verification/memory-qdrant.md)

### 4.5 验收（Domain）

```text
存储 L4 角色外貌 → search "眼睛颜色" → 命中琥珀色；延迟 <1s（文件层）
writer gate --phase 1 不破坏；pytest tests/memory/ 通过
```

---

## 5. 视频三层节点（CURSOR 独有，写回 SOLO）

见 `cursor-novel-video/references/VIDEO-PIPELINE-NODES.md`：

- **Brain**：Gemma/LLaVA QC + REPAIR（≤3 轮）
- **Still**：Wan T2V length=1（`COMFYUI_STILL_BACKEND=wan`）
- **Motion**：Wan I2V（`comfyui_i2v.py`）

---

## 6. FICUS 协作模板索引

| 模板 | 场景 | 纪要章节 |
| --- | --- | --- |
| A 架构师 | 启动节点、划定边界 | §3 模板 A |
| B 提示词工程师 | 单文件精确实现 | §3 模板 B |
| C 审计员 | 提交前验收 | §3 模板 C |
| D 运维 | Sprint 增量 | §3 模板 D |
| E 领域专家 | 端到端业务验证 | §3 模板 E |
| F 根因分析 | 测试失败调试 | §3 模板 F |

---

## 7. 缺口优先级（仍未解决）

| P0 | P1 | P2 |
| --- | --- | --- |
| Qdrant 生产部署 | Playwright 发布 | 数据看板 |
| Brain QC 自动 REPAIR 循环 | BGM 情绪匹配 | REST API |
| 文档 D 安全 CHK 进 CI | MCP 扩展 | 雪花法 CLI |

---

最后更新：2026-06-07 — Sprint 1.2 Qdrant + M3E 混合检索与 sync/probe
