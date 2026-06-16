# Novel Suite 阶段 C5 执行报告 — 默认关闭 Adapter 原型包

**日期：** 2026-06-01  
**范围：** 默认关闭、纯本地 dry-run、manifest/plan 生成；不调用外部服务或专业软件。

---

## 目标

将 C3 handoff 文档样例转化为可测试的 adapter skeleton：读取 `cold_case_echo_short_drama` handoff 样本，输出本地 plan/outline/import
plan，证明未来可接外部工具，但当前 `enabled=false`、`external_call_performed=false`。

---

## 读取上下文

- `docs/NOVEL_SUITE_C3_HANDOFF_SPEC_REPORT.md`
- `docs/NOVEL_SUITE_C4_PRODUCT_LAYER_REPORT.md`
- `novel-suite/video-production/handoff/**`
- `novel-suite/video-production/examples/cold_case_echo_short_drama/handoff/**`
- `COMMERCIAL_RELEASE_GATE.md`、`THIRD_PARTY_POLICY.md`

---

## 新增代码文件

| 文件 | 说明 |
| --- | --- |
| `src/novel_suite/video_production/__init__.py` | 包入口 |
| `src/novel_suite/video_production/adapters/policy.py` | `AdapterPolicy`、`default_adapter_policy`、`assert_dry_run_only` |
| `src/novel_suite/video_production/adapters/comfyui.py` | ComfyUI dry-run → `comfyui_plan.json` |
| `src/novel_suite/video_production/adapters/otio.py` | OTIO-like outline → `otio_outline.generated.json`（不导入 opentimelineio） |
| `src/novel_suite/video_production/adapters/davinci.py` | DaVinci import plan → `davinci_import_plan.json` |
| `src/novel_suite/video_production/cli.py` | `run_adapter_dry_run`、example/output 路径解析 |
| `src/novel_suite/cli.py` | 挂载 `video-production adapter dry-run` 子命令 |
| `src/novel_suite/core/errors.py` | C5 错误码 |
| `tests/test_video_production_adapters.py` | 11 项覆盖 |

---

## Adapter policy

- 默认：`enabled=false`、`dry_run=true`、`allow_external_call=false`
- `assert_dry_run_only()` 对 `enabled=True` 或 `allow_external_call=True` 抛 `AdapterPolicyError`
- 不支持 `--execute` 参数

---

## Dry-run artifacts

输出目录：`.tmp/novel-suite-c5/`（相对 monorepo 根）

| Adapter | 输入 | 输出 | 关键字段 |
| --- | --- | --- | --- |
| ComfyUI | `prompt_batch.sample.jsonl`、`keyframe_to_video_manifest.sample.json` | `comfyui_plan.json` | `mode=dry_run_plan_only`, `prompt_count`, `planned_nodes` |
| OTIO | `timeline_handoff.sample.json` | `otio_outline.generated.json` | `mode=dry_run_outline_only`, `tracks/clips/transitions` |
| DaVinci | `timeline_mapping.sample.csv`、`asset_manifest.sample.json` | `davinci_import_plan.json` | `mode=dry_run_import_plan_only`, `media_pool_candidates` |

所有 artifact：`enabled=false`、`external_call_performed=false`。

---

## CLI 验证

```powershell
novel-suite video-production adapter dry-run --adapter comfyui --example cold_case_echo_short_drama --output
.tmp/novel-suite-c5 --json
novel-suite video-production adapter dry-run --adapter otio --example cold_case_echo_short_drama --output
.tmp/novel-suite-c5 --json
novel-suite video-production adapter dry-run --adapter davinci --example cold_case_echo_short_drama --output
.tmp/novel-suite-c5 --json
```

| 命令 | 结果 |
| --- | --- |
| comfyui dry-run | ✅ `VIDEO_PRODUCTION_ADAPTER_DRY_RUN_OK` |
| otio dry-run | ✅ `VIDEO_PRODUCTION_ADAPTER_DRY_RUN_OK` |
| davinci dry-run | ✅ `VIDEO_PRODUCTION_ADAPTER_DRY_RUN_OK` |

---

## 测试结果

| 套件 | 结果 |
| --- | --- |
| `pytest tests/test_video_production_adapters.py -q` | **11 passed** |
| C4+C5 回归 | **31 passed** |
| `pytest -m "not ffmpeg"` | **436 passed**, 2 skipped |

网络/socket：`urllib.request.urlopen`、`socket.socket` monkeypatch 未触发。

---

## 未执行动作

- 未发起网络请求或 socket 连接 ComfyUI
- 未启动 DaVinci / Premiere / AE / Blender
- 未执行 FFmpeg
- 未导入 `opentimelineio`
- 未修改 SOLO / Reasonix
- 未发布 / 上传 / 外发
- 商业发布仍受 `COMMERCIAL_RELEASE_GATE.md` 约束

---

## 下一阶段建议

1. **C6：** 短剧样例包商业前置审查
2. **C7：** AI短剧生产销售页与交付包前置审查
3. **C8：** 真实 adapter 启用前安全评审（需人工确认）
