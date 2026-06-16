# Novel Suite 阶段 B1 执行报告

**执行日期：** 2026-06-10  
**目标：** 工程接入 + 合规门禁包（CLI doctor、JSON Schema、Rules Pack 分发、合规三件套、测试）  
**规格源（只读）：** AI_Workspace_OS `小说视频工具链三项目评审_20260610`  
**写入目标：** `G:\CURSOR`  
**禁止：** 修改 SOLO/Reasonix、调用第三方服务、发布外发

## 计划新增/修改文件

| 路径 | 动作 |
| --- | --- |
| `novel-suite/core/contracts/*.schema.json` | 新增 ×4 |
| `src/novel_suite/core/contracts.py` | 新增 |
| `src/novel_suite/core/rules_pack.py` | 新增 |
| `src/novel_suite/writer/doctor.py` | 修改 |
| `src/novel_suite/cli.py` | 修改 |
| `platforms/install-rules-packs.ps1` | 新增 |
| `platforms/install-skills.ps1` | 提示行 |
| `LICENSE` | 新增 |
| `THIRD_PARTY_NOTICES.md` | 新增 |
| `THIRD_PARTY_POLICY.md` | 新增 |
| `tests/test_novel_suite_core_contracts.py` | 新增 |
| `tests/test_rules_pack_distribution.py` | 新增 |

## 执行结果

### Step 2 — JSON Schema 草案

- ✅ `story_bible.schema.json`
- ✅ `chapter_context.schema.json`
- ✅ `scene_to_video.schema.json`
- ✅ `asset_registry.schema.json`

### Step 3–4 — contracts 模块 + doctor

- ✅ `novel-suite doctor --core-contracts --json` → `DOCTOR_CORE_OK`

### Step 5 — Rules Pack 分发

- ✅ `platforms/install-rules-packs.ps1`（`-DryRun`, `-Copy`, `-UseIdeDirs`, `-Agents`）

### Step 6–7 — 合规三件套 + ebooklib 标注

- ✅ `LICENSE` (MIT draft, 98jinshanshan)
- ✅ `THIRD_PARTY_NOTICES.md`
- ✅ `THIRD_PARTY_POLICY.md`
- ✅ ebooklib 仍 in dev optional — 文档明确禁入核心

### Step 8–9 — 测试

（测试结果在 Cursor 执行后追加于下方「测试记录」节）

## ebooklib 状态

仍在 `pyproject.toml` `[project.optional-dependencies] dev`。未删除；`THIRD_PARTY_POLICY.md` §6 记录隔离要求。

## 测试记录

| 命令 | 结果 |
| --- | --- |
| `pytest tests/test_novel_suite_core_contracts.py tests/test_rules_pack_distribution.py -q` | **10 passed** |
| `pytest -m "not ffmpeg"` | **359 passed**, 2 skipped, 2 deselected |
| `novel-suite doctor --core-contracts --json` | exit 0, `DOCTOR_CORE_OK` |
| `install-rules-packs.ps1 -DryRun` | 6 agents validated |
