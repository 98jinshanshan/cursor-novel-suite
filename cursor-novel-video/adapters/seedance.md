# Seedance / Replicate B-roll (optional)

Set `REPLICATE_API_TOKEN` and use super-video-maker patterns:

```bash
# Example (requires replicate package)
replicate run bytedance/seedance-2.0 prompt="cinematic documentary scene..." duration=5
```

Pipeline slot in `video-scene-drama`: after local Ken Burns fails QC,
agent may call this adapter.

Reference: [super-video-maker-skill](https://github.com/Bomx/super-video-maker-skill)
