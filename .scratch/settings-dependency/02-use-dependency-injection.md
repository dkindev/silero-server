---
title: "Use dependency injection for settings in consumers"
labels:
  - ready-for-human
created: 2026-05-19
---

## Parent

.scratch/settings-dependency/01-add-cached-get-settings.md

## What to build

Update `main.py` and routers to use `get_settings()` instead of importing `settings` directly.

- Update `src/main.py` to call `get_settings()` instead of using `settings` module-level instance
- Export `SettingsDep` from `src/routers/__init__.py`
- Update `src/routers/process.py` to use `settings: SettingsDep` parameter instead of importing `settings` directly

## Acceptance criteria

- [x] main.py uses get_settings()
- [x] SettingsDep exported from routers/__init__.py
- [x] process.py uses SettingsDep parameter
- [x] All routes continue to work correctly