---
title: "Add cached get_settings() dependency"
labels:
  - ready-for-human
created: 2026-05-19
---

## What to build

Add `lru_cache` to Settings initialization via a `get_settings()` dependency function for use with FastAPI's `Depends`.

- Add `@lru_cache` decorator to a `get_settings()` function in `src/config.py`
- Add `SettingsDep` type alias: `Annotated[Settings, Depends(get_settings)]`
- Import required modules: `functools.lru_cache`, `typing.Annotated`, `fastapi.Depends`

Keep existing `settings = Settings()` for backward compatibility.

## Acceptance criteria

- [x] `get_settings()` returns cached Settings instance
- [x] `SettingsDep` type alias available for import
- [x] Tests pass (if any)