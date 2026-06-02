# Novel Suite 目录架构规范

**layout-version：** `2.0.0`（2026-06-03）  
**速查：** [WORKSPACE-LAYOUT.md](./WORKSPACE-LAYOUT.md)；物理树以本文 §2 为准  
**关联：**

- [STRUCTURE-STANDARDS.md](./STRUCTURE-STANDARDS.md)
- [NODE-EXECUTION-CONTRACT.md](./NODE-EXECUTION-CONTRACT.md)
- [layout-phase-map.json](./layout-phase-map.json)

---

## 1. 设计目标

| 目标 | 手段 |
| --- | --- |
| 左侧不再像「四套 skills」 | IDE 安装目录 **整夹隐藏** + 只编辑 canonical `cursor-novel-*/skills/` |
| Phase 0–9 可导航 | `docs/workflow/` + `layout-phase-map.json` 机器可读映射 |
| 节点加厚可验收 | `canon/nodes/phase-N.completion.json` 路径写死在映射表 |
| 版本可迭代 | `layout-version` 升级时走 §5 迁移规则 |

---

## 2. 权威目录树（layout 2.0.0）

```text
<NOVEL_SUITE_ROOT>/
├── .novel-suite-root          # 根标记 + layout-version（§4）
├── README.md · AGENTS.md
├── cursor-novel-writer/       # 【编辑区 A】小说 skills + engine + templates + examples
│   ├── skills/                # ★ 唯一 Skill 源码
│   ├── engine/
│   ├── schema/
│   ├── templates/
│   ├── examples/demo-novel/
│   └── tests/
├── cursor-novel-video/        # 【编辑区 B】视频 skills + engine
│   ├── skills/
│   └── engine/
├── docs/                        # 【编辑区 C】规范 / 工作流 / 审计
│   ├── standards/               # 含本文、NEC、STRUCTURE
│   ├── workflow/                # Phase 0–9 导航
│   ├── plans/
│   └── verification/
├── novels/                      # 【数据区】用户小说（registry + <slug>/）
├── intel/                       # 【数据区】选品 radar / concepts
├── platforms/                   # install-skills.ps1 · patch-update
├── .vscode/ · .github/          # 工具配置（可隐藏部分，见 §3）
└── [隐藏·勿编辑] .agents/ .qoder/ .trae/ .cursor/skills/
```

**禁止在根目录新增：** `phase-0/`、`skills/`（扁平）、第二套 `engine/`。

---

## 3. 资源管理器可见性（VS Code / Cursor）

| 路径 | 可见 | 原因 |
| --- | --- | --- |
| `cursor-novel-writer/skills/` | ✅ | Canonical |
| `cursor-novel-video/skills/` | ✅ | Canonical |
| `docs/workflow/` | ✅ | Phase 导航 |
| `.agents/` `.qoder/` `.trae/` | ❌ exclude | 安装镜像 |
| `.cursor/skills/` | ❌ exclude | 安装镜像 |
| `.cursor/rules/` | ✅ | Agent 规则 |
| `.pytest_cache/` `.venv/` | ❌ exclude | 环境 |

配置：根目录 [.vscode/settings.json](../../.vscode/settings.json)（重载窗口生效）。

可选：打开 [novel-suite.code-workspace](../../novel-suite.code-workspace) 多根视图（按编辑区折叠）。

---

## 4. 版本字段（根标记文件）

`.novel-suite-root` 键值：

| 键 | 含义 | 当前 |
| --- | --- | --- |
| `novel-suite-root` | 根识别 | `1` |
| `suite-version` | 安装/同步工具链 | `2026.06.03-nec` |
| `layout-version` | **目录架构** semver | `2.0.0` |
| `nec-version` | 节点执行契约 | `1.0` |

**检测旧文档：** `novel suite doctor` 比对根标记 `layout-version` 与
`layout-phase-map.json`；不一致则 WARN。

---

## 5. 目录联动与版本迭代规则

### 5.1 何时 bump `layout-version`

| 变更类型 | 示例 | bump |
| --- | --- | --- |
| **PATCH** `x.y.Z` | 仅文档、exclude 模式 | Z+1 |
| **MINOR** `x.Y.0` | 新增 `canon/nodes/`、新 schema | Y+1，写 `docs/audit/YYYY-MM-DD-layout-migration.md` |
| **MAJOR** `X.0.0` | skills 挪到 repo 根、删除 `novels/` | X+1，需迁移脚本 |

### 5.2 Phase 节点 → 路径映射更新流程

1. 改 [layout-phase-map.json](./layout-phase-map.json)（机器可读）
2. 同步 [docs/workflow/README.md](../workflow/README.md) 与受影响 Skill `node-dispatch.md`
3. 若 manifest 路径变：bump `nec-version` + 更新 `node-completion.schema.json`
4. bump `layout-version`（MINOR 起）并更新 `.novel-suite-root`
5. `suite doctor` 必须通过；pytest smoke 通过

### 5.3 废弃路径（layout 2.0.0 起）

| 废弃 | 替代 |
| --- | --- |
| 根目录 `phase-0/` | `intel/radar/` + Skill `novel-market-scan` |
| 手改 `.trae/skills/*` | 改 `cursor-novel-writer/skills/` + `install-skills.ps1` |
| 仅聊天出表无 `*.completion.json` | NEC 禁止（见 NODE-EXECUTION-CONTRACT） |

---

## 6. 与 NEC 批次交付的对应

| 批次 | 目录/引擎成果 |
| --- | --- |
| A | `docs/workflow/`、`skills/README.md`、WORKSPACE-LAYOUT |
| B | `canon/nodes/phase-{1,2,3}.completion.json`、`novel node sync` |
| C–E | 继续 phase-4…9 + verification 矩阵 |

---

*旧版 WORKSPACE-LAYOUT 仍保留简短说明，但以本文为架构权威。*
