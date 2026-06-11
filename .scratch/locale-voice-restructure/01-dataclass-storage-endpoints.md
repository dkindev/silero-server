---
title: "Restructure Locale/VoiceConfig/TTSConfigModel dataclasses, storage, and endpoints"
labels:
  - ready-for-agent
created: 2026-06-11
---

## What to build

Restructure the locale and voice data model from a nested hierarchy to a flat schema that supports richer `Locale` metadata in the future (e.g., locale-specific preprocessing, default sample rate).

### Changes across all layers

**Dataclasses (`src/tts/models.py`):**
- `Locale`: add `name: str`, remove `voices: dict[str, VoiceConfig]`
- `VoiceConfig`: add `locale: str` (references `locale.name`)
- `TTSConfigModel`: change `locales: dict[str, Locale]` → `locales: list[Locale]`, add `voices: list[VoiceConfig]`

**Config storage (`src/tts/config_storage.py`):**
- YAML `_load_config_model`: build `list[Locale]` from locale keys and `list[VoiceConfig]` from nested voice entries (each gets `locale=locale_key`).
- Internal state becomes `_locales: dict[str, tuple[Locale, list[VoiceConfig]]]` keyed by `locale.name`.
- Abstract `SileroTTSConfigStorage.get_locales() -> list[Locale]` (was `tuple[str, ...]`)
- Abstract `SileroTTSConfigStorage.get_voices() -> list[VoiceConfig]` (was `dict[str, list[VoiceConfig]]`)
- `_filter_enabled`: filter voices by enabled model, then filter locales to only those with available voices (preserving empty-locale behavior).
- `_build_voices`: no longer needed — `get_voices()` flattens from `_locales` values.
- `has_locale`, `has_voice`: adapt to lookup in `_locales` dict.
- `get_voice_config`: search across all `_locales` values for matching locale+voice_name.

**Endpoints:**
- `/locales`: iterate `get_locales()` → `l.name`, join with newline. Same output format.
- `/voices`: iterate `get_voices()` → `f"{vc.voice_name} {vc.locale} {vc.gender}"`. Same output format.

**Tests:**
- Update all `Locale(...)` and `VoiceConfig(...)` constructor calls in `test_tts_models.py`, `test_config_storage.py`, `test_routers.py`.
- Update mock return values for `get_locales()` and `get_voices()` to match new types.

## Acceptance criteria

- [x] `Locale` has `name: str`, no `voices` field
- [x] `VoiceConfig` has `locale: str`
- [x] `TTSConfigModel` has `locales: list[Locale]` and `voices: list[VoiceConfig]`
- [x] YAML config loading constructs the new shapes correctly, including `speaker` defaulting to `voice_name`
- [x] `_filter_enabled` excludes voices referencing disabled models, and excludes locales with no available voices
- [x] `SileroTTSConfigStorage.get_locales() -> list[Locale]`
- [x] `SileroTTSConfigStorage.get_voices() -> list[VoiceConfig]`
- [x] `has_locale`, `has_voice`, `get_voice_config` work correctly against the new internal structure
- [x] `GET /locales` returns same plain-text output (one locale per line)
- [x] `GET /voices` returns same Mary-TTS format (`{voice_name} {locale} {gender}` per line)
- [x] `GET /process` validates locale and voice correctly via the adapted `has_locale`/`has_voice`
- [x] All existing tests pass without modification (beyond constructor/mock updates)

## Blocked by

None — can start immediately
