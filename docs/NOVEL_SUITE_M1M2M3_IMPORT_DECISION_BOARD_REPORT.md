# Novel Suite 合并报告：M1 试用决策 + M2 冻结决策 + M3 法律评审委员会

**日期：** 2026-06-01  
**任务：** L 阶段预检后的决策记录与 board 模板 — **非**读取真实材料、**非**改 gate。

---

## M1 试用材料预检决策记录结论

- `trial-import-decision-record/`（11 文件）：通过/拒收、PII 决策、backlog CR、`no_auto_backlog_apply_policy.md`
- `.tmp/novel-suite-m/trial-import-decision-record/`：空决策目录
- `preflight_result_available=false`、`import_approved=false`、`backlog_auto_applied=false`
- CLI：`trial-import-decision-record validate`

## M2 冻结材料预检决策记录结论

- `freeze-import-decision-record/`（11 文件）：manifest/checksum 验收、tag followup、`release_prohibited_policy.md`
- `tag_created=false`、`import_approved=false`
- CLI：`freeze-import-decision-record validate`

## M3 法律材料预检决策与评审委员会结论

- `legal-import-decision-board/`（12 文件）：board CR、签字需求、`release_gate_changed=false`
- `board_decision_available=false`、`auto_blocker_closure=false`
- CLI：`legal-import-decision-board validate`

---

## 仍然 blocked

真实人工材料尚未导入；决策模板不关闭 B01–B05；`verdict=blocked` 不变。

---

## 验证

| 命令 | 结果 |
| --- | --- |
| 三个 M validate | OK |
| product / candidate validate | OK |
| 专项 pytest | 12 passed |

---

## 未执行

- 未读取私密目录、未导入真实材料
- 无 git tag / zip / release / gate 修改
- 无法律结论、无 blocker 关闭

---

## 下一阶段（执行包级）

1. **N1**：人工完成 L1 预检后，按 M1 填写决策记录至 `.tmp-m/`
2. **N2**：人工完成 L2 预检后，按 M2 记录冻结决议；tag 仍仅人工执行
3. **N3**：人工完成 L3 预检后，按 M3 召开评审委员会审议 CR
