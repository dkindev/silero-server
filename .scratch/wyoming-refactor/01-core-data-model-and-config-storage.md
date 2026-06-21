---
title: "Core data model & config storage"
labels:
  - ready-for-agent
created: 2026-06-18
---

## What to build

Update the core dataclasses (`Voice`, `Locale`, `TTSResult`) and the config storage layer to support the new domain model, then rename the config file.

### Dataclass changes (`src/tts/models.py`)

- `Voice`: add `id: str` field — format `{locale}-{model}-{name}`, computed during config loading
- `Locale`: add `language: str` field — language code (e.g. `"ru"`)
- `TTSResult.audio`: change type from `io.BytesIO` to `bytes` (raw PCM, not WAV)
- `TTSResult`: add `bytes_per_sample: int` and `channels: int` fields

### Config storage changes (`src/tts/config_storage.py`)

- **ABC** `SileroTTSConfigStorage`:
  - Remove: `has_locale_in_voices`, `has_voice`, `get_locales_in_voices`
  - Change: `get_voice(locale_name, voice_name)` → `get_voice(voice_id)`
  - Add: `get_locale(name) -> Locale`
- **YAML impl** `SileroTTSYamlConfigStorage`:
  - Rewrite `_load_config_model` to parse locales/voices nested under models (no separate top-level `locales` key)
  - Compute `Voice.id = f"{locale}-{model}-{name}"` when constructing Voice objects
  - Build `_voices_by_id: dict[str, Voice]` for O(1) `get_voice(voice_id)` lookups
  - Build `_locales: dict[str, Locale]` keyed by locale name

### Config file rename

- Rename `silero-to-mary-config.yml` → `config.yml`
- The YAML structure is already valid: locales are nested under their model, with each locale referencing its model and containing voice entries

## Acceptance criteria

- [x] `Voice` has `id: str` computed as `{locale}-{model}-{name}` when loaded from YAML
- [x] `Locale` has `language: str` field populated from YAML
- [x] `TTSResult.audio` is `bytes` type (not `io.BytesIO`)
- [x] `TTSResult` has `bytes_per_sample` and `channels` fields
- [x] `SileroTTSConfigStorage` ABC has new method signatures (removed old methods, changed `get_voice`, added `get_locale`)
- [x] `SileroTTSYamlConfigStorage` parses merged YAML structure correctly
- [x] `get_voice(voice_id)` returns the correct `Voice` by its computed ID
- [x] `get_locale(name)` returns `Locale` with correct `language` field
- [x] Config file renamed from `silero-to-mary-config.yml` to `config.yml`
- [x] All existing config_storage tests pass with updated signatures and fixtures

## Blocked by

None — can start immediately
