# 修辞与句式模式（De-AI）

`deai_audit.py --modes rhetoric` 加载下方 `regex` 块。

## 规则

| ID | 说明 | 严重度 |
| --- | --- | --- |
| rhetoric.not_a_but_b | 不是…而是… | warn |
| rhetoric.is_not_but | 是…不是…而是… | warn |
| rhetoric.however_stack | 同段多次然而/但是 | warn |
| rhetoric.parallel_three | 连续排比 ≥3 | warn |
| rhetoric.decorative_simile | 像一[枚滴场道根盏把张封]… | 装饰性「像一枚/像一滴…」比喻 |
| rhetoric.simile_of_measure | 像…的…（工整喻体） | 「像…的…」模板比喻 |
| rhetoric.classical_ink | 朱砂、宣纸、白宣纸 | 古风喻体堆饰（网文 AI 常见） |

```regex
rhetoric.not_a_but_b|不是[^，。！？\n]{1,40}，?而是|「不是…而是…」
rhetoric.is_not_but|是[^，。！？\n]{1,30}，?不是[^，。！？\n]{1,30}，?而是|「是…不是…而是…」
rhetoric.however_stack|(然而|但是|不过|可是)([^。！？\n]*)(然而|但是|不过|可是)|转折词堆叠
rhetoric.parallel_three|([^。！？\n]{8,}[，、]){2,}[^。！？\n]{8,}|长排比
rhetoric.decorative_simile|像一[枚滴场道根盏把张封节块]([^，。！？\n]{2,30})|装饰性「像一枚/像一滴…」比喻
rhetoric.simile_of_measure|像[^，。！？\n]{2,18}的[^，。！？\n]{2,18}|「像…的…」模板比喻
rhetoric.classical_ink|朱砂|落在[^。！？\n]{0,12}白宣纸|古风 ink 喻体
```
