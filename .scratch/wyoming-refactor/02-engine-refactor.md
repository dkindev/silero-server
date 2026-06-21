---
title: "Engine refactor"
labels:
  - ready-for-agent
created: 2026-06-18
---

## What to build

Refactor `SileroTTSEngine` to remove the HTTP-oriented `process()` method, add audio format constants, and change `synthesize_pcm_chunks()` to accept a `voice_id` and yield `TTSResult` objects with raw PCM audio and full metadata.

### Changes (`src/tts/engine.py`)

- Add module-level constants: `BYTES_PER_SAMPLE = 2`, `CHANNELS = 1`
- Remove `process()` method and the `_chunks_to_wav_bytes()` helper (dead code)
- Change `synthesize_pcm_chunks(self, text, locale_name, voice_name, input_type)` → `synthesize_pcm_chunks(self, text, voice_id, input_type)`:
  - Look up voice internally via `self._storage.get_voice(voice_id)`
  - Extract `locale_name = voice.locale` for text preprocessor selection
  - Extract `speaker = voice.speaker` for model inference
  - Each chunk yields `TTSResult(audio=pcm_bytes, sample_rate=..., model=..., bytes_per_sample=BYTES_PER_SAMPLE, channels=CHANNELS)`
- Fix stale comment in `_get_lock()` referencing "FastAPI"

### Test changes (`tests/test_engine.py`)

- Replace all `process()` calls with iteration over `synthesize_pcm_chunks()`
- Update assertions: `TTSResult.audio` is now `bytes` (not `io.BytesIO`), assert `bytes_per_sample == 2` and `channels == 1`
- Update `Voice` construction to include `id` field
- Update `Locale` construction to include `language` field
- Keep all existing test coverage for sample rate selection, model caching, semaphore limiting, device fallback

## Acceptance criteria

- [x] `BYTES_PER_SAMPLE = 2` and `CHANNELS = 1` are defined as module constants in `engine.py`
- [x] `process()` method is removed
- [x] `_chunks_to_wav_bytes()` helper is removed
- [x] `synthesize_pcm_chunks(text, voice_id, input_type)` accepts a single `voice_id` string
- [x] Voice lookup is internal: calls `self._storage.get_voice(voice_id)` and uses `voice.locale` for preprocessing
- [x] Each yielded `TTSResult` has `audio: bytes` (raw PCM), `bytes_per_sample == 2`, `channels == 1`
- [x] All existing engine tests pass with updated signatures and assertions
- [x] Sample rate selection, model caching, semaphore, and device fallback behavior is preserved

## Blocked by

- /workspaces/python/.scratch/wyoming-refactor/01-core-data-model-and-config-storage.md
