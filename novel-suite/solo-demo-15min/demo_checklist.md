# 15 分钟 Demo 验收清单

完成下列项即视为 P1 demo 路线试跑通过（个人开发者自查，非商业验收）。

## 理解与定位

- [ ] 读过 `novel-suite/README.md` 与 delivery-hub 入口
- [ ] 知道 PP-001 是新手起点
- [ ] 知道视频化当前为规格入口，非真实成片

## 边界

- [ ] `commercial_release_allowed=false` 已确认
- [ ] `verdict=blocked` 已确认
- [ ] 未执行 tag/zip/release/上传/发布
- [ ] 未调用 FFmpeg / TTS / 图像 / 平台 API

## 只读 CLI（可选）

- [ ] `novel-suite product validate --json` 返回 OK
- [ ] `novel-suite commercial-release-candidate validate --json` 仍 blocked
- [ ] `novel-suite solo-demo-15min validate --json` 返回 OK

## 反馈

- [ ] 已复制 `multi-ide-dry-run-feedback/feedback_template.md` 并起草一条本地记录
- [ ] `external_call_performed=false` 自查为真

## 时长

- [ ] 总耗时约 15 分钟（±5 分钟可接受）
