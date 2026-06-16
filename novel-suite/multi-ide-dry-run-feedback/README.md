# Multi-IDE Dry-Run Feedback（P3）

**多 IDE dry-run 试用反馈模板统一** — 本地收集，**无**遥测、**无**自动上传。

```yaml
telemetry_collected: false
external_call_performed: false
private_project_read: false
```

## 文件

| 文件 | 用途 |
| --- | --- |
| [feedback_template.md](feedback_template.md) | 统一反馈表 |
| [ide_matrix.md](ide_matrix.md) | IDE 覆盖矩阵 |
| [local_collection_policy.md](local_collection_policy.md) | 本地保存策略 |
| [no_telemetry_policy.md](no_telemetry_policy.md) | 无遥测声明 |

## 与 C10 关系

继承 `novel-suite/multi-ide-trials/` 试用范围，但将反馈格式压缩为 P3 统一模板，供 P1 demo 环节 5 与后续 Q 阶段承接。

## 校验

```powershell
novel-suite multi-ide-dry-run-feedback validate --json
```
