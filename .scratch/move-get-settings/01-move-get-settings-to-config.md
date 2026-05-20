---
title: "Move get_settings() to config.py"
labels:
  - ready-for-agent
created: 2026-05-20
---

## What to build

Move the `get_settings()` function from `src/main.py` to `src/config.py`, keeping the `@lru_cache` decorator. Update the import in `main.py` and remove the local definition. Keep `SettingsDep` type alias in `main.py`.

## Acceptance criteria

- [ ] `get_settings()` defined in `src/config.py` with `@lru_cache`
- [ ] `src/main.py` imports `get_settings` from `src.config`
- [ ] `SettingsDep` remains in `main.py` (re-export for backward compatibility)
- [ ] `routers/process.py` continues to work (imports `SettingsDep` from `main.py`)
- [ ] App starts and runs correctly

## Blocked by

None - can start immediately