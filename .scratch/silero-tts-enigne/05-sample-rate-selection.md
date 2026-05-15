---
title: "05: Sample rate selection logic"
labels:
  - completed
created: 2026-05-15
completed: 2026-05-15
---

## Parent

.scratch/silero-tts-enigne/silero-tts-engine.md

## What to build

Update `silero_tts_engine.py` sample rate selection logic and add test coverage. Logic (sorted/deduplicated list):
- Empty/None sample_rates → use TTS_SAMPLE_RATE
- Single element → use that element
- TTS_SAMPLE_RATE > max → clamp to max
- TTS_SAMPLE_RATE < min → use min
- Exact match → use that value
- Not in list → use highest value less than TTS_SAMPLE_RATE

## Acceptance criteria

- [x] Implementation handles all 7 cases
- [x] Tests cover all scenarios

## Blocked by

None - can start immediately