# 修辞与句式模式（De-AI）

`deai_audit.py --modes rhetoric` 加载下方 `regex` 块。

## 规则

| ID | 说明 | 严重度 |
| --- | --- | --- |
| rhetoric.not_a_but_b | 不是…而是… | warn |
| rhetoric.is_not_but | 是…不是…而是… | warn |
| rhetoric.however_stack | 同段多次然而/但是 | warn |
| rhetoric.parallel_three | 连续排比 ≥3 | warn |

```regex
rhetoric.not_a_but_b|不是[^，。！？\n]{1,40}，?而是|「不是…而是…」
rhetoric.is_not_but|是[^，。！？\n]{1,30}，?不是[^，。！？\n]{1,30}，?而是|「是…不是…而是…」
rhetoric.however_stack|(然而|但是|不过|可是)([^。！？\n]*)(然而|但是|不过|可是)|转折词堆叠
rhetoric.parallel_three|([^。！？\n]{8,}[，、]){2,}[^。！？\n]{8,}|长排比
```
