# RealGen-1 已废止

**取代方：** RealPipeline-2B · `novels/novel-837dd4f1`

RealGen-1 旁路（`cold_case_echo_realgen_01`、错误角色林澄/程砚、1334 字模板章、动态文字卡视频）**不得**再作为验收依据。

## 正确入口

```powershell
.\.venv\Scripts\python.exe -m novel_suite.cli realpipeline validate --project novels/novel-837dd4f1 --json
.\.venv\Scripts\python.exe -m novel_suite.cli realpipeline run --project novels/novel-837dd4f1 --json
```

## 证据链

- 小说：`novels/novel-837dd4f1/chapters/02_双签.md`（≥2500 CJK，林骁/陈琪）
- NVP：`novels/novel-837dd4f1/reports/NVP-*.result.md`
- 总评：`novels/novel-837dd4f1/reports/realpipeline_2b_nvp_manifest.json`（overall_grade **C**，视频短板）

`realgen-demo run` CLI 返回 `REALGEN_DEMO_DEPRECATED`。
