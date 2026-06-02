---
title: "Add `enabled` field to Model + storage-level filtering"
labels:
  - ready-for-agent
created: 2026-06-02
---

## What to build

Add `enabled: bool = True` to the `Model` dataclass (`src/tts/models.py`). Add `_filter_enabled()` to `SileroTTSYamlConfigStorage` (`src/tts/config_storage.py`) that produces a filtered `TTSConfigModel` containing only enabled models, their voices, and non-empty locales. Call it during `__init__` before building `_locales` and `_voices`.

This affects all public query methods — `get_voices()`, `get_locales()`, `has_locale()`, `has_voice()`, `get_voice_config()`, `get_model_info()` — they transparently reflect the filtered state.

## Acceptance criteria

- [x] `Model` dataclass has `enabled: bool = True` field
- [x] `SileroTTSYamlConfigStorage` filters out disabled models at construction time (when built from programmatic `TTSConfigModel`)
- [x] `get_voices()` excludes voices that reference a disabled model
- [x] `get_locales()` excludes locales that have zero enabled voices
- [x] `has_voice(locale, voice)` returns `False` for voices that reference a disabled model
- [x] `has_locale(locale)` returns `False` for orphaned locales
- [x] `get_model_info(name)` raises `KeyError` for a disabled model

## Blocked by

None — can start immediately
