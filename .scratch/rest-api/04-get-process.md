---
title: "GET /process endpoint"
labels:
  - needs-triage
created: 2026-05-19
---

## What to build

Implement `GET /process` for text-to-speech synthesis.

- Create `src/routers/process.py` with GET endpoint
- Accept query params: INPUT_TEXT, INPUT_TYPE, OUTPUT_TYPE, LOCALE, VOICE, AUDIO
- Validate text length against TTS_MAX_TEXT_LENGTH (400 if exceeded)
- Pass params to engine.process()
- Return raw WAV bytes with `Content-Type: audio/wav`, `Content-Disposition: inline`

## Acceptance criteria

- [x] GET /process?INPUT_TEXT=hello&LOCALE=ru_RU&VOICE=silero-v5_5_ru-aidar returns WAV
- [x] 400 for text exceeding max length
- [x] 400 for invalid locale/voice (handled by engine)
- [x] Content-Type: audio/wav
- [x] Content-Disposition: inline

## Blocked by

01-router-infrastructure