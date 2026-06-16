# No Auto Import Policy（O1 承接）

## 禁止

- 将 O1 填报 ingest 到长期库或公开 sample
- 将 `import_approved` 改为 true
- 自动应用 backlog / 修改产品代码
- 修改 `final-release-gate.md` 或关闭 B01–B05
- 读取 O2/O3 目录或用户其他私密路径

## 固定边界

```yaml
import_approved: false
backlog_auto_applied: false
commercial_release_allowed: false
verdict: blocked
```

只读承接仅生成校验报告与候选清单，不等于批准导入。
