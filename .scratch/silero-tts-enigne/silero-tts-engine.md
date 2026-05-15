---
title: "Stage 1: SileroTTSEngine Implementation"
labels:
  - ready-for-agent
created: 2026-05-14
---

## Problem Statement

The TTS API requires a SileroTTSEngine to wrap the Silero TTS library and provide a clean interface for the REST endpoints. Currently, no such engine exists.

## Solution

Implement `src/tts/silero_tts_engine.py` with:
- Init from `TTSConfig` (frozen dataclass) and `TTSConfigModel` (typed from YAML)
- Public API: `get_locales()`, `get_voices()`, `process()`
- Lazy model loading via torch.hub.load() with per-model concurrency
- Typed `TTSResult` and exception hierarchy

## User Stories

1. As the TTS server, I want to initialize the engine at startup, so it is ready to use
2. As an API client, I want `GET /locales` to return available locales
3. As an API client, I want `GET /voices` to return voices in Mary-TTS format
4. As an API client, I want `POST /process` to return WAV audio
5. As the engine, I want lazy model loading for fast startup
6. As the engine, I want per-model concurrency limits to prevent OOM
7. As the engine, I want input validation with typed errors
8. As the engine, I want sample rate clamping for limited models
9. As the engine, I want to pass SSML directly to Silero
10. As the engine, I want async-safe synthesis (to_thread)
11. As the router, I want typed exceptions mapped to HTTP codes

## Implementation Decisions

- **Init**: receives `TTSConfig` and `TTSConfigModel` dataclasses
- **get_locales() → tuple[str, ...]**
- **get_voices() → tuple[str, ...]** (Mary-TTS format: `"{voice} {locale} {gender}"`)
- **process(text, locale, voice, input_type, output_type) → TTSResult**
- **TTSResult**: `audio: bytes`, `sample_rate: int`, `model: str`
- **Exceptions**: `TTSEngineError` → `InvalidLocaleError` (400), `InvalidVoiceError` (400), `InvalidInputTypeError` (400), `InvalidOutputTypeError` (406), `TTSProcessingError` (500)
- **Concurrency**: per-model semaphores created lazily, limit from `TTS_MAX_CONCURRENT_PER_LOCALE`
- **Model loading**: torch.hub.load() directly (torch manages cache)
- **Synthesis**: `asyncio.to_thread()` + `model.apply_tts(text, speaker, sample_rate)`
- **Sample rate**: clamp to model's max if configured exceeds it
- **SSML**: pass directly to model (no preprocessing)
- **Config dataclasses**: `TTSConfigModel(models, locales)`, `Model(language, sample_rates)`, `Locale(voices)`, `VoiceConfig(speaker, model, gender)`

## Testing Decisions

- Test external behavior only, not internal implementation
- Mock Silero model and torch.hub.load
- Test file: `tests/test_silero_tts_engine.py`
- Prior art: `tests/config.py` for test structure

## Out of Scope

- Text preprocessing, HTTP router, health check, CORS, shutdown, rate limiting, auth