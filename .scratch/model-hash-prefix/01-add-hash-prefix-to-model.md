---
title: "Add optional hash_prefix to Model for .pt integrity verification"
labels:
  - ready-for-agent
created: 2026-06-11
---

## What to build

Add an optional `hash_prefix: str | None` field to the `Model` dataclass.
When set, the hash prefix is passed to `torch.hub.download_url_to_file` as
the `hash_prefix` parameter when downloading the model's `.pt` file, enabling
SHA256 integrity verification at download time.

Changes across three layers:

1. **Dataclass** (`src/tts/models.py`): Add `hash_prefix: str | None = None`
   to `Model`.

2. **Config storage** (`src/tts/config_storage.py`): Parse optional
   `hash_prefix` from YAML model entries via `m.get("hash_prefix") or None`
   (coerces empty string to None).

3. **Engine** (`src/tts/engine.py`):
   - `_resolve_model` gains `hash_prefix: str | None = None` parameter.
   - Pass it as `hash_prefix=hash_prefix` to `torch.hub.download_url_to_file`.
   - `_load_model_async` reads `model_info.hash_prefix` and forwards it.

No changes to `config.py` / `Settings`, or `silero-to-mary-config.yml`.

## Acceptance criteria

- [x] `Model` dataclass has `hash_prefix: str | None = None` field (frozen)
- [x] `hash_prefix` defaults to `None` when omitted from YAML
- [x] `SileroTTSYamlConfigStorage` parses `hash_prefix` from YAML
- [x] `_resolve_model` accepts optional `hash_prefix` and passes it to
      `torch.hub.download_url_to_file`
- [x] `_load_model_async` reads `model_info.hash_prefix` and passes it through
- [x] All existing tests pass (mocks use `*a, **kw` and are compatible)

## Blocked by

None — can start immediately
