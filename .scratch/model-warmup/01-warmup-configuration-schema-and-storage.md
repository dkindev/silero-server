---
title: "Add warmup configuration schema + storage method"
labels:
  - ready-for-agent
created: 2026-06-03
---

## What to build

Add the `warmup` field to the model configuration schema and a method to retrieve models from storage. This is the foundation for the model warmup feature — no behavioral change at startup yet.

Changes across three layers:

1. **Dataclass** (`src/tts/models.py`): Add `warmup: bool = False` to the `Model` dataclass.

2. **Config storage** (`src/tts/config_storage.py`):
   - Parse `warmup` from YAML config: `m.get("warmup", False)` in `_load_config_model`
   - Add abstract method `get_models() -> dict[str, Model]` to `SileroTTSConfigStorage` ABC
   - Implement `get_models()` in `SileroTTSYamlConfigStorage` returning `self._config_model.models`

3. **Config file** (`silero-to-mary-config.yml`): Set `warmup: true` on `v5_5_ru` as a usage example.

## Acceptance criteria

- [x] `Model` dataclass has `warmup: bool = False` field (frozen, default false)
- [x] `SileroTTSYamlConfigStorage` parses `warmup: true` from YAML and constructs `Model(warmup=True)`
- [x] `warmup` defaults to `False` when omitted from YAML
- [x] `SileroTTSConfigStorage` ABC declares `get_models() -> dict[str, Model]`
- [x] `SileroTTSYamlConfigStorage.get_models()` returns all enabled models (post-filtering) with their `warmup` field
- [x] `silero-to-mary-config.yml` has `warmup: true` on `v5_5_ru`

## Blocked by

None — can start immediately
