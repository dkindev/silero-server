---
title: "04: Unit tests for SileroTTSEngine"
labels:
  - needs-triage
created: 2026-05-14
---

## Parent

`.scratch/silero-tts-enigne/silero-tts-engine.md`

## What to build

Write comprehensive unit tests for SileroTTSEngine.

## Acceptance criteria

- [x] Test get_locales() returns correct tuple
- [x] Test get_voices() returns correct Mary-TTS format
- [x] Test process() with valid inputs returns TTSResult
- [x] Test process() with invalid locale raises InvalidLocaleError
- [x] Test process() with invalid voice raises InvalidVoiceError
- [x] Test process() with invalid input_type raises InvalidInputTypeError
- [x] Test process() with non-AUDIO output_type raises InvalidOutputTypeError
- [x] Test sample rate clamping
- [x] Test per-model concurrency limits

## Blocked by

- `.scratch/silero-tts-enigne/02-engine-init.md`
- `.scratch/silero-tts-enigne/03-process-method.md`

## Completed

All 24 tests pass in `tests/test_silero_tts_engine.py`.