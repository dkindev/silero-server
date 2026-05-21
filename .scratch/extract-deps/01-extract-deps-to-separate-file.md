---
title: "Extract FastAPI dependencies to src/deps.py"
labels:
  - ready-for-agent
created: 2026-05-21
---

## What to build

Extract `get_engine()`, `EngineDep`, and `SettingsDep` from `src/main.py` into a new `src/deps.py` file. Update all import sites across routers and tests to import from the new module. No re-exports from `main.py`.

## Acceptance criteria

- [x] `src/deps.py` exists with `get_engine()`, `EngineDep`, and `SettingsDep` definitions
- [x] `src/main.py` no longer defines those three items (lifespan and CORS config remain unchanged)
- [x] All 3 routers (`process.py`, `voices.py`, `locales.py`) import from `src.deps`
- [x] All test references to `EngineDep` and `get_engine` import from `src.deps`
- [x] `pytest` passes
- [x] App starts and all endpoints respond correctly

## Blocked by

None - can start immediately
