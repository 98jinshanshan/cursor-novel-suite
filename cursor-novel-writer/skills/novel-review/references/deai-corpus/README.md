# De-AI 审计语料库（NEC-11）

| 文件 | 用途 |
| --- | --- |
| [lexicon.txt](./lexicon.txt) | 机器加载（1100+ 行）；`deai_audit.py --modes lexicon` |
| [lexicon-high-frequency.md](./lexicon-high-frequency.md) | 人类可读分类与来源说明 |
| [rhetoric-patterns.md](./rhetoric-patterns.md) | 修辞/句式正则库 |
| [narrative-patterns.md](./narrative-patterns.md) | 叙事手法正则库 |

维护：运行 `engine/scripts/generate_deai_lexicon.py` 重建 `lexicon.txt`（会覆盖手工追加的装饰比喻词，重建后请对照 `lexicon-high-frequency.md`
补回「装饰比喻」类）。

**装饰比喻（2026-06）：** `rhetoric.decorative_simile` / `rhetoric.classical_ink` — 见 `rhetoric-patterns.md`；人类替换表见
`narrative-patterns.md` §装饰比喻。
