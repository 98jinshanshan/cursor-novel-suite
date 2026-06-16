# 无遥测政策

```yaml
telemetry_collected: false
external_call_performed: false
private_project_read: false
```

## 声明

Novel Suite P3 反馈模板：

- **不**自动采集用户行为或聊天内容
- **不**上传反馈到外部服务
- **不**启用 product analytics 或 IDE 遥测钩子
- **不**读取 `G:\SOLO小说项目`、`G:\Reasonix\SOLO小说视频项目` 或用户未授权私密目录

## Agent 义务

- 仅使用用户显式提供的反馈文本
- 不得声称已「汇总全网试用数据」
- validate CLI 仅检查本仓库内文档与 sample JSON

## 用户义务

- 自行保管本地反馈文件
- 粘贴前做脱敏
- 若 `external_call_performed=true`，须在反馈中如实注明（通常不应在 P 阶段发生）
