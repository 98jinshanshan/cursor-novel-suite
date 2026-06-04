# 叙事手法模式（De-AI）

`deai_audit.py --modes narrative`

```regex
narrative.felt_wave|感到[^。！？\n]{0,12}(涌上心头|袭来|席卷)|情绪模板句
narrative.as_you_know|正如你所知|众所周知|不难看出|值得注意的是|说明体
narrative.summary_ending|总而言之|综上所述|可以说|从某种意义上|段末升华
narrative.eyes_density|目光|眼神|视线|眸光|眼神链（见密度统计）
```

同章「目光/眼神/视线」>4 次时脚本追加 `narrative.eyes_density` warn。
