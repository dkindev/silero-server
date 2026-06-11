---
title: "Migrate models.yml URL and hash to env-based config"
labels:
  - ready-for-agent
created: 2026-06-11
---

## What to build

Move the hardcoded `MODELS_YML_URL` and `MODELS_YML_HASH` module-level constants from the engine into env-based configuration. Add `TTS_MODELS_YML_URL` and `TTS_MODELS_YML_HASH` to Pydantic Settings, add corresponding fields to `TTSConfig`, plumb through the dependency wiring, and update the engine to read them from config instead of module-level constants. Update tests to construct `TTSConfig` directly with the computed hash instead of patching module-level constants. Update `.env.example` and `CONTEXT.md`.

The two new env vars default to the same values as the current hardcoded constants, so behavior is identical when no env vars are set.

### Details from prototyping session

**Naming:** `TTS_MODELS_YML_URL` and `TTS_MODELS_YML_HASH` (consistent with existing `TTS_*` pattern).

**Types:** In `TTSConfig`, `models_yml_url: str` and `models_yml_hash: str | None`.

**Engine:** `_get_models_data(yml_path, models_yml_url, models_yml_hash)` and `_download_models_yml(file_path, models_yml_url, models_yml_hash)` receive values as parameters. Engine stores them as instance attributes from `self._config`. The engine's `_resolve_model()` passes them through.

**Tests:** Replace 4 `unittest.mock.patch("src.tts.engine.MODELS_YML_HASH", ...)` calls with `TTSConfig(models_yml_hash=_hash_models_yml(...), ...)` — no module-level patching needed.

## Acceptance criteria

- [x] `TTS_MODELS_YML_URL` and `TTS_MODELS_YML_HASH` can be set via `.env`
- [x] Default values match the current hardcoded constants
- [x] Engine reads URL and hash from `TTSConfig` instead of module-level constants
- [x] All existing tests pass without patching `src.tts.engine.MODELS_YML_HASH`
- [x] `.env.example` includes both new variables
- [x] `CONTEXT.md` configuration table includes both new variables

## Blocked by

None — can start immediately
