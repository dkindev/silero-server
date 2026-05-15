---
title: "04: Unit tests for SileroTTSEngine"
labels:
  - ready-for-agent
created: 2026-05-14
---

## Parent

`.scratch/silero-tts-enigne/silero-tts-engine.md`

## What to build

Write comprehensive unit tests for SileroTTSEngine.

## Acceptance criteria

- [ ] Test get_locales() returns correct tuple
- [ ] Test get_voices() returns correct Mary-TTS format
- [ ] Test process() with valid inputs returns TTSResult
- [ ] Test process() with invalid locale raises InvalidLocaleError
- [ ] Test process() with invalid voice raises InvalidVoiceError
- [ ] Test process() with invalid input_type raises InvalidInputTypeError
- [ ] Test process() with non-AUDIO output_type raises InvalidOutputTypeError
- [ ] Test sample rate clamping
- [ ] Test per-model concurrency limits

## Blocked by

- `.scratch/silero-tts-enigne/02-engine-init.md`
- `.scratch/silero-tts-enigne/03-process-method.md`