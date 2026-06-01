---
title: "Define SileroTTSConfigStorage interface and SileroTTSYamlConfigStorage implementation"
labels:
  - ready-for-agent
created: 2026-05-26
---

## What to build

Create `src/tts/config_storage.py` with two classes:

**`SileroTTSConfigStorage`** — abstract base class defining the interface for querying the TTS voice/locale configuration model. Six methods:

- `has_locale(locale: str) -> bool`
- `has_voice(locale: str, voice_name: str) -> bool`
- `get_locales() -> tuple[str, ...]`
- `get_voices() -> tuple[str, ...]`
- `get_voice_config(locale: str, voice_name: str) -> VoiceConfig`
- `get_model_info(model_name: str) -> Model`

**`SileroTTSYamlConfigStorage`** — concrete implementation backed by a `TTSConfigModel` (loaded from YAML file or passed directly).

- Constructor: `__init__(self, config_path_or_model: str | TTSConfigModel)`
  - If `str`: load YAML from that path (moves `_load_config_model` logic into this class as a private method)
  - If `TTSConfigModel`: use directly
- Compute `_locales` tuple and `_voices` tuple (Mary-TTS format `"{voice_name} {locale} {gender}"`) at init time via a private `_build_voices` method
- Implement all six interface methods

This file is purely additive — no existing code is touched.

## Acceptance criteria

- [x] `SileroTTSConfigStorage` is an abstract base class in `src/tts/config_storage.py`
- [x] `SileroTTSYamlConfigStorage` inherits from it with a working constructor accepting `str | TTSConfigModel`
- [x] All six methods return correct data matching the existing engine's behavior
- [x] `get_voices()` returns Mary-TTS format strings `"{voice_name} {locale} {gender}"`
- [x] Unit tests cover: both constructor paths (YAML file, in-memory model), all six methods, empty config edge case, multiple locales/voices
- [x] No existing code is modified

## Blocked by

None — can start immediately
