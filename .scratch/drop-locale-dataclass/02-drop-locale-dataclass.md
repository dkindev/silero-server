---
title: "Drop Locale dataclass and related infrastructure"
labels:
  - ready-for-agent
created: 2026-06-18
---

## What to build

Remove the `Locale` frozen dataclass and all code that depends on it. Replace `Locale.language` lookups with `get_language_from_locale_string(voice.locale)`.

Changes span all layers:

**Schema (`src/tts/models.py`):**
- Remove `Locale` dataclass
- Remove `locales: list[Locale]` from `TTSConfigModel`

**Config storage (`src/tts/config_storage.py`):**
- Remove `get_locale()` from `SileroTTSConfigStorage` abstract base class
- Remove `self._locales` dict and `get_locale()` from `SileroTTSYamlConfigStorage`
- Remove `locales_list` and `Locale(...)` construction from `_load_config_model`
- Remove locale filtering (the `locales_with_enabled_voices` set and `filtered_locales` list) from `_filter_enabled`
- Remove `Locale` from import line

**Application (`src/main.py`):**
- Replace `storage.get_locale(voice.locale).language` with `get_language_from_locale_string(voice.locale)`
- Import `get_language_from_locale_string`

**Tests:**
- `tests/test_tts_models.py`: remove `TestLocale` class, remove `Locale` from import
- `tests/test_config_storage.py`: remove `TestGetLocale` class, remove `test_locale_language_derived_from_locale_name_not_yaml_key`, remove `Locale` from import, drop `locales=` from all `TTSConfigModel(...)` calls
- `tests/test_engine.py`: remove `make_locale()` helper, remove `Locale` from import, drop `locales=` from all `TTSConfigModel(...)` calls

**Documentation (`CONTEXT.md`):**
- Update **Locale** definition: it is no longer a separate entity but a string field on `Voice`; the language is extracted via a helper

## Acceptance criteria

- [x] `Locale` dataclass no longer exists in `src/tts/models.py`
- [x] `locales` field removed from `TTSConfigModel`
- [x] `get_locale()` removed from both storage abstract base and concrete class
- [x] YAML config loading no longer builds `Locale` objects or a locales list
- [x] `_filter_enabled` no longer filters locales (models/voices still filtered by enabled)
- [x] `main.py` uses `get_language_from_locale_string(voice.locale)` instead of `storage.get_locale(voice.locale).language`
- [x] All tests pass (`pytest tests/`)
- [x] All lint checks pass (`ruff check src tests`)
- [x] `CONTEXT.md` Locale entry updated

## Blocked by

- `.scratch/drop-locale-dataclass/01-add-locale-string-helper.md`
