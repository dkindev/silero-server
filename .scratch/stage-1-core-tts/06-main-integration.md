---
title: "Stage 1: Main.py Integration"
labels:
  - ready-for-agent
created: 2026-05-12
---

## Parent

docs/stages/1.md

## What to build

Integrate all components in `src/main.py`:
- Import and include voices_router, process_router, locales_router
- Wire Silero wrapper into app state or lifespan context
- CORS middleware via TTS_ALLOWED_ORIGINS
- Lifespan: initialize Silero wrapper on startup, close on shutdown
- Graceful shutdown with TTS_SHUTDOWN_TIMEOUT

## Acceptance criteria

- [ ] All routers (/locales, /voices, /process) mounted under /api/v1/
- [ ] Silero wrapper initialized at startup, closed at shutdown
- [ ] CORS middleware enabled with TTS_ALLOWED_ORIGINS
- [ ] Graceful shutdown drains in-flight requests up to TTS_SHUTDOWN_TIMEOUT
- [ ] Application starts successfully with valid config

## Blocked by

- Stage 1: GET /api/v1/locales Endpoint
- Stage 1: GET /api/v1/voices Endpoint
- Stage 1: GET+POST /api/v1/process Endpoint