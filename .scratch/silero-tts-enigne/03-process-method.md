---
title: "03: process() with lazy model loading"
labels:
  - completed
created: 2026-05-14
completed: 2026-05-15
---

## Parent

`.scratch/silero-tts-enigne/silero-tts-engine.md`

## What to build

Implement process() method with validation, per-model semaphores, lazy model loading via torch.hub.load(), asyncio.to_thread() synthesis, sample rate clamping.

## Acceptance criteria

- [x] process() validates locale exists → InvalidLocaleError
- [x] process() validates voice exists for locale → InvalidVoiceError
- [x] process() validates input_type TEXT/SSML → InvalidInputTypeError
- [x] process() validates output_type AUDIO → InvalidOutputTypeError
- [x] Per-model semaphores created lazily, limit from config
- [x] torch.hub.load() called on first request per model
- [x] Synthesis runs in asyncio.to_thread()
- [x] Sample rate clamped to model's max if exceeded
- [x] Returns TTSResult with audio bytes, sample_rate, model

## Blocked by

- `.scratch/silero-tts-enigne/01-config-exceptions.md`