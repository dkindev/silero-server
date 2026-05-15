---
title: "01: Config dataclasses, Exceptions, TTSResult"
labels:
  - ready-for-agent
created: 2026-05-14
---

## Parent

`.scratch/silero-tts-enigne/silero-tts-engine.md`

## What to build

Define typed dataclasses for config (TTSConfigModel, Model, Locale, VoiceConfig), exception hierarchy (TTSEngineError base + 5 subclasses), and TTSResult result object.

## Acceptance criteria

- [x] TTSConfigModel with models and locales dicts
- [x] Model dataclass with language and sample_rates
- [x] Locale dataclass with voices dict
- [x] VoiceConfig dataclass with speaker, model, gender
- [x] TTSEngineError base exception
- [x] InvalidLocaleError, InvalidVoiceError, InvalidInputTypeError, InvalidOutputTypeError, TTSProcessingError subclasses
- [x] TTSResult dataclass with audio, sample_rate, model fields

## Blocked by

None - can start immediately