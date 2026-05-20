---
title: "Move load_config_model to engine module"
labels:
  - ready-for-agent
created: 2026-05-20
---

## Parent

(None - standalone refactor)

## What to build

Refactor so that `models.py` contains only data classes, with loading logic moved to the engine module.

- Move `load_config_model()` from `src/tts/models.py` to `src/tts/silero_tts_engine.py` as `_load_config_model()`
- Update `create_silero_engine` signature from `create_silero_engine(config, config_model)` to `create_silero_engine(config, config_path: str)` — internally loads config and passes model to engine
- Update `src/main.py` imports: remove `load_config_model`, pass `app_settings.TTS_CONFIG_PATH` instead of pre-loaded `config_model`
- Run tests to verify

## Acceptance criteria

- [x] `_load_config_model()` exists in `silero_tts_engine.py` (private function)
- [x] `load_config_model` removed from `models.py`, data classes remain
- [x] `create_silero_engine` accepts `config_path: str` and loads config internally
- [x] `main.py` updated: no longer imports `load_config_model`, passes config path to engine
- [x] Tests pass

## Blocked by

None - can start immediately