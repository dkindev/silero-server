---
title: "Remove delegating methods from SileroTTSEngine, route callers, tests, and docs"
labels:
  - ready-for-agent
created: 2026-05-26
---

## What to build

Remove `has_locale()`, `has_voice()`, `get_locales()`, `get_voices()` from `SileroTTSEngine`. All external callers must use `engine.get_storage().method()` instead.

Engine's own `process()` switches from `self.has_locale()` / `self.has_voice()` to `self._storage.has_locale()` / `self._storage.has_voice()` directly.

Route files `process.py`, `locales.py`, `voices.py` switch from `engine.method()` to `engine.get_storage().method()`.

`test_routers.py` mock patterns change from `mock_engine.has_locale = ...` to `mock_engine.get_storage.return_value.has_locale.return_value = ...`.

Remove duplicate test classes from `test_silero_tts_engine.py` that test storage behavior through the engine (already covered by `test_config_storage.py`).

Update `CONTEXT.md` to document the methods on `SileroTTSConfigStorage` and `get_storage()` on the engine, removing the old method references from `SileroTTSEngine`.

## Acceptance criteria

- [x] `SileroTTSEngine` no longer has `has_locale`, `has_voice`, `get_locales`, `get_voices` methods
- [x] `process()` on engine uses `self._storage.*` directly for locale/voice validation
- [x] `/process` endpoint validates locale/voice via `engine.get_storage().has_locale()` / `.has_voice()`
- [x] `/locales` endpoint returns locales via `engine.get_storage().get_locales()`
- [x] `/voices` endpoint returns voices via `engine.get_storage().get_voices()`
- [x] `test_routers.py` uses `mock_engine.get_storage.return_value.*` patterns
- [x] Duplicate test classes `TestHasLocale`, `TestHasVoice`, `TestGetLocales`, `TestGetVoices`, `TestCaching` removed from `test_silero_tts_engine.py`
- [x] `CONTEXT.md` reflects the new API surface
- [x] All tests pass

## Blocked by

None — can start immediately
