---
title: "03: process() with lazy model loading"
labels:
  - ready-for-agent
created: 2026-05-14
---

## Parent

`.scratch/silero-tts-enigne/silero-tts-engine.md`

## What to build

Implement process() method with validation, per-model semaphores, lazy model loading via torch.hub.load(), asyncio.to_thread() synthesis, sample rate clamping.

## Acceptance criteria

- [ ] process() validates locale exists → InvalidLocaleError
- [ ] process() validates voice exists for locale → InvalidVoiceError
- [ ] process() validates input_type TEXT/SSML → InvalidInputTypeError
- [ ] process() validates output_type AUDIO → InvalidOutputTypeError
- [ ] Per-model semaphores created lazily, limit from config
- [ ] torch.hub.load() called on first request per model
- [ ] Synthesis runs in asyncio.to_thread()
- [ ] Sample rate clamped to model's max if exceeded
- [ ] Returns TTSResult with audio bytes, sample_rate, model

## Blocked by

- `.scratch/silero-tts-enigne/01-config-exceptions.md`