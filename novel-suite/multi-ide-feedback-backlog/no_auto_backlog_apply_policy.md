# No Auto Backlog Apply Policy（Q3）

```yaml
feedback_imported: false
backlog_auto_applied: false
telemetry_collected: false
private_project_read: false
```

## 规则

- **不得**自动修改仓库代码、PromptPack、门禁字段
- **不得**自动关闭 blocker 或改 `commercial_release_allowed`
- **不得**采集 telemetry 或上传反馈
- **不得**读取未授权私密项目
- 反馈仅来自用户粘贴或 `.tmp/novel-suite-q/` 内用户填写文件
- `feedback_imported=false` 直至 R1 授权只读承接

## 承接路径

用户填写 → `.tmp/novel-suite-q/` → R1 只读承接 → R2 修订方案 → 人工确认应用
