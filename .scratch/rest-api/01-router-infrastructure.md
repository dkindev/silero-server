---
title: "REST API Router Infrastructure"
labels:
  - needs-triage
created: 2026-05-19
---

## What to build

Create the base router infrastructure for the Mary-TTS compatible REST API.

- Add global exception handler in `src/routers/__init__.py` for TTSEngineError subclasses
- Configure CORS middleware from config via `add_middleware`
- Create `get_engine()` dependency for `Depends()` injection
- Wire engine initialization in `main.py` lifespan context manager

## Acceptance criteria

- [x] TTSEngineError subclasses return JSON error with correct status code
- [x] CORS allows configured origins
- [x] Engine injectable via `Depends(get_engine)`
- [x] Engine initialized at startup via lifespan

## Blocked by

None - can start immediately