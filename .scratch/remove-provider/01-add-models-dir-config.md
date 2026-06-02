---
title: "Add models_dir config surface"
labels:
  - ready-for-agent
created: 2026-06-02
---

## What to build

Add a `TTS_MODELS_DIR` environment variable and corresponding `models_dir` field on `TTSConfig`, wired through `deps.py`. The value is stored but not yet consumed — this is the config foundation for removing the standalone `SileroTTSModelProvider`.

Specific changes:
- Add `TTS_MODELS_DIR: str = ".models/silero"` to `Settings` in `src/config.py`
- Add `models_dir: str = ".models/silero"` to `TTSConfig` dataclass in `src/tts/models.py`
- Pass `models_dir=settings.TTS_MODELS_DIR` in the `TTSConfig(...)` call in `src/deps.py`
- Add `TTS_MODELS_DIR` to the config table in `CONTEXT.md`

## Acceptance criteria

- [x] `TTS_MODELS_DIR` env var is accepted by Settings with correct default
- [x] `TTSConfig(models_dir=...)` stores and returns the value
- [x] `deps.add_engine()` passes the value from Settings to TTSConfig
- [x] All existing tests pass unchanged
- [x] `CONTEXT.md` documents the new env var

## Blocked by

None — can start immediately.
