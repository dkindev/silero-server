---
title: "Replace config_model with storage in SileroTTSEngine"
labels:
  - ready-for-agent
created: 2026-05-26
---

## What to build

Modify `SileroTTSEngine` to depend on `SileroTTSConfigStorage` instead of `TTSConfigModel` directly.

**Constructor change:**
- Replace `config_model: TTSConfigModel` parameter with `storage: SileroTTSConfigStorage`
- Store as `self._storage`
- Remove `self._config_model`, `self._locales`, `self._voices` attributes

**Config query delegation:**
- `has_locale()`, `has_voice()`, `get_locales()`, `get_voices()` delegate to `self._storage`
- Remove `_build_voices()` method from engine

**process() update:**
- Replace `self._config_model.locales[locale].voices[voice]` → `self._storage.get_voice_config(locale, voice)`
- Replace `self._config_model.models[model_name]` → `self._storage.get_model_info(model_name)`

**Removals from `silero_tts_engine.py`:**
- `_load_config_model()` module-level function (already migrated to storage)
- `_build_voices()` method (already migrated to storage)
- `create_silero_engine()` factory function

**Add to engine:**
- `get_storage() -> SileroTTSConfigStorage` accessor method

**Test updates:**
- All tests that used `create_silero_engine()` must construct the engine directly:
  ```python
  storage = SileroTTSYamlConfigStorage(config_path_or_model)
  provider = SileroTTSModelProvider()
  engine = SileroTTSEngine(config=config, storage=storage, provider=provider)
  ```
- Mock patterns for `SileroTTSModelProvider` and `torch.package.PackageImporter` stay unchanged
- All existing assertions should continue to pass

## Acceptance criteria

- [x] `SileroTTSEngine.__init__` accepts `storage: SileroTTSConfigStorage` and no longer accepts `config_model: TTSConfigModel`
- [x] `has_locale`, `has_voice`, `get_locales`, `get_voices` delegate to storage
- [x] `process()` uses `storage.get_voice_config()` and `storage.get_model_info()` for config lookups
- [x] `_load_config_model`, `_build_voices`, `create_silero_engine` are removed from `silero_tts_engine.py`
- [x] `get_storage()` accessor added to engine
- [x] All engine tests pass with direct construction (no `create_silero_engine` calls)
- [x] All router tests pass unchanged

## Blocked by

- #1 — Define SileroTTSConfigStorage interface and SileroTTSYamlConfigStorage implementation
