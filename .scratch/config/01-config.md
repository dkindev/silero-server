---
title: "Stage 1: TTS Config Pydantic Settings"
labels:
  - ready-for-agent
created: 2026-05-12
---

## What to build

Extend Pydantic Settings in `src/config.py` with new TTS_* configuration fields:
- `TTS_SAMPLE_RATE`: Literal[8000, 16000, 22050, 24000, 48000] = 48000
- `TTS_MAX_TEXT_LENGTH`: int = 1000 (min=1, max=10000)
- `TTS_ALLOWED_ORIGINS`: str = "*"
- `TTS_SHUTDOWN_TIMEOUT`: int = 10
- Rename existing `tts_device` → `TTS_DEVICE` for consistency

Validation must reject invalid device, sample rate, and timeout values at startup with a clear error and non-zero exit.

Update `.env.example` with all five new variables.

## Acceptance criteria

- [x] Settings class accepts TTS_SAMPLE_RATE, TTS_MAX_TEXT_LENGTH, TTS_ALLOWED_ORIGINS, TTS_SHUTDOWN_TIMEOUT
- [x] TTS_DEVICE renamed from tts_device
- [x] Invalid TTS_SAMPLE_RATE values (e.g., 44100) cause startup failure with clear error
- [x] Invalid TTS_SHUTDOWN_TIMEOUT values (e.g., 0, negative) cause startup failure with clear error
- [x] .env.example contains all five TTS_* variables with example values

## Blocked by

None - can start immediately