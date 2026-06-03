---
title: "Implement model warmup in engine and wire to lifespan"
labels:
  - ready-for-agent
created: 2026-06-03
---

## What to build

Implement the actual model warmup mechanism in `SileroTTSEngine` and wire it into the application lifespan. This slice depends on the `warmup` field and `get_models()` method from slice 1.

Changes across three layers:

1. **Engine model-loading extension** (`src/tts/silero_tts_engine.py`):
   - `_resolve_model()` return type changes from `(path, rates)` to `(path, rates, example_text, speakers)`:
     - `example_text`: string from `tts_models -> <language> -> <model_name> -> latest -> example`
     - `speakers`: `dict[str, str]` — speaker name → example text, from `tts_models -> <language> -> <model_name> -> latest -> speakers`. Empty dict if no speakers key exists.
   - `_load_model_async()` return type changes from `CachedModel` to `(CachedModel, example_text, speakers)`
   - `process()` unpacks the new return types: `cached, _, _`

2. **Warmup method** (`src/tts/silero_tts_engine.py`):
   - Add `warmup()` method that:
     - Acquires the cache lock, returns immediately if cache is non-empty
     - Gets models via `self._storage.get_models()`, filters to `warmup=True`, caps at `self._config.max_models`
     - For each model: loads it, runs a dummy synthesis call using the example text
       - If `speakers` dict is non-empty: use first speaker entry's example text + speaker name
       - Otherwise: use `example_text` + `cached.model.speakers[0]`
     - Silently swallows per-model exceptions (model will lazy-load on first use instead)

3. **Lifespan** (`src/main.py`):
   - After `add_engine(app)`, retrieve the engine from `app.state` and call `await engine.warmup()`

## Acceptance criteria

- [x] `_resolve_model()` returns 4-tuple `(path, rates, example_text, speakers)` without breaking existing callers
- [x] `_load_model_async()` returns 3-tuple `(CachedModel, example_text, speakers)` without breaking existing callers
- [x] `process()` works correctly after unpacking new return types
- [x] `warmup()` loads models with `warmup: true` and runs dummy synthesis on each
- [x] `warmup()` uses per-speaker examples from the `speakers` dict when available, falls back to global `example` + `model.speakers[0]`
- [x] `warmup()` silently handles a model loading failure and does not prevent server startup
- [x] `warmup()` is a no-op when cache is already populated
- [x] Lifespan calls `warmup()` after engine creation
- [x] Existing tests still pass after engine return type changes

## Blocked by

- 01-warmup-configuration-schema-and-storage
