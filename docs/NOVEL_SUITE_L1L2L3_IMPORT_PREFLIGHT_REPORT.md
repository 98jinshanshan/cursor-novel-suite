# Novel Suite 合并报告：L1 试用导入预检 + L2 冻结导入预检 + L3 法律导入预检

**日期：** 2026-06-01  
**任务：** 导入前预检规范 — **非**读取私密目录、**非**导入真实材料、**非**发布。

---

## L1 人工试用结果导入预检结论

- `trial-result-import-preflight/`（12 文件）：允许路径、PII 拒收、schema/backlog 预检、拒收码
- `.tmp/novel-suite-l/trial-result-import-preflight/`：空预检暂存目录
- `input_results_available=false`、`preflight_passed=false`、`revision_auto_applied=false`
- CLI：`trial-result-import-preflight validate`

## L2 版本冻结会议结果导入预检结论

- `freeze-decision-import-preflight/`（12 文件）：manifest/checksum、人工 tag 决策格式、no-release
- `input_decision_available=false`、`tag_created=false`
- CLI：`freeze-decision-import-preflight validate`

## L3 法律/合规会议结果导入预检结论

- `legal-decision-import-preflight/`（11 文件）：counsel/签字/CR 格式、法律意见边界
- `input_legal_decision_available=false`、`auto_blocker_closure=false`
- CLI：`legal-decision-import-preflight validate`

---

## 仍然 blocked

B01–B04 open；预检不导入、不关闭；`verdict=blocked` 不变。

---

## 验证

| 命令 | 结果 |
| --- | --- |
| 三个 L validate | OK |
| product / candidate validate | OK |
| 专项 pytest | 12 passed |

---

## 未执行

- 未读取私密目录/全盘
- 未导入真实反馈/会议/法律材料
- 无 git tag / zip / release
- 无 blocker 关闭 / 无法律结论

---

## 下一阶段（执行包级）

1. **M1**：人工将脱敏试用结果放入 `.tmp-k`，按 L1 清单预检后填 import decision
2. **M2**：人工将冻结会议记录预检；若通过且批准 tag，**人工**本地执行
3. **M3**：人工将法律材料在安全路径预检，CR 提交评审委员会
