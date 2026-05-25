---
title: "Model cache eviction — setting, tests, doc"
labels:
  - ready-for-agent
created: 2026-05-25
---

## What to build

Add `TTS_MAX_MODELS` env var (ge=1, default 2) to control how many Silero models stay cached in memory. When the cache is full and a new model is requested, the least-recently-used model is evicted and its torch resources freed.

Delivered end-to-end: env var → `TTSConfig` → engine eviction logic → verified via black-box test.

## Changes

| File | Change |
|------|--------|
| `src/config.py` | Add `TTS_MAX_MODELS: int = Field(2, ge=1)` |
| `src/main.py` | Wire `app_settings.TTS_MAX_MODELS` → `TTSConfig(max_models=...)` |
| `.env.example` | Add `TTS_MAX_MODELS=2` |
| `CONTEXT.md` | Add config table row + Model Cache section |
| `tests/test_config.py` | Update `seven` → `eight` test, add 4 new setting tests |
| `tests/test_env_example.py` | Add `TTS_MAX_MODELS` to `required_vars` |
| `tests/test_tts_models.py` | Add `TestTTSConfig` dataclass tests |
| `tests/test_silero_tts_engine.py` | Add `max_models=2` to all `TTSConfig()` calls; refactor ~16 `engine._provider` patches → class-level `SileroTTSModelProvider` mocks; delete `TestLoadModel` (broken); rewrite private-access assertions; add eviction test |
| `tests/test_engine_factory.py` | Add `max_models=2` to all `TTSConfig()` calls; refactor / delete private-method tests |

## Acceptance criteria

- [x] `TTS_MAX_MODELS=5` in `.env` is accepted; `TTS_MAX_MODELS=0` and `TTS_MAX_MODELS=-1` are rejected at startup
- [x] `TTS_MAX_MODELS` default is 2 in both `Settings` and the configuration table in `CONTEXT.md`
- [x] All existing tests pass after refactoring (no `engine._provider` patches, no `_load_model` calls, no `engine._cached_models` access)
- [x] Eviction test: `max_models=1`, call `process()` for model A, then model B, then model A again → `get_model` called 3 times (A loaded, B loaded + evicts A, A re-loaded)

## Blocked by

None — can start immediately.
