---
title: "Add add_engine(app) to deps.py and call from lifespan()"
labels:
  - ready-for-agent
created: 2026-05-26
---

## What to build

Add a convenience function `add_engine(app: FastAPI)` to `src/deps.py` that creates the full engine stack and stores it on `app.state.engine`. Then use it in `src/main.py`, replacing the inline engine creation.

**In `src/deps.py`:**
```python
def add_engine(app: FastAPI):
    settings = get_settings()
    config = TTSConfig(
        device=settings.TTS_TORCH_DEVICE,
        sample_rate=settings.TTS_SAMPLE_RATE,
        max_models=settings.TTS_MAX_MODELS,
        max_concurrent_per_model=settings.TTS_MAX_CONCURRENT_PER_MODEL,
    )
    storage = SileroTTSYamlConfigStorage(settings.TTS_CONFIG_PATH)
    provider = SileroTTSModelProvider()
    app.state.engine = SileroTTSEngine(config=config, storage=storage, provider=provider)
```

New imports: `SileroTTSYamlConfigStorage`, `TTSConfig`, `SileroTTSModelProvider`, `SileroTTSEngine`.

**In `src/main.py`:**
- Replace the body of `lifespan()` — call `setup_torch()` then `add_engine(app)` instead of creating the engine inline
- `setup_torch()` stays as a separate call (global PyTorth config, not engine-specific)
- Remove imports: `create_silero_engine`, `TTSConfig`, `get_settings`

Shutdown logic stays unchanged: `get_engine(app.state)` then `await engine.shutdown()`.

## Acceptance criteria

- [x] `add_engine()` is defined in `src/deps.py` and wires config+storage+provider+engine together
- [x] `setup_torch()` remains a separate call in `lifespan()`
- [x] `lifespan()` in `src/main.py` calls `add_engine(app)` instead of inline engine creation
- [x] Unused imports removed from `src/main.py`
- [x] App starts, routes resolve, `/locales`, `/voices`, `/process` endpoints work as before
- [x] No test changes required (routes mock the engine, don't construct one)

## Blocked by

- #2 — Replace config_model with storage in SileroTTSEngine
