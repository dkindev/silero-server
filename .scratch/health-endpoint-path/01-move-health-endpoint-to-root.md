---
title: "Move health endpoint to root path"
labels:
  - ready-for-agent
closed: 2026-06-04
created: 2026-06-04
---

## What to build

Move the health endpoint from `/api/v1/health` to `/health` for Mary-TTS API compatibility. Mary TTS defines `/health` at root; all other endpoints (`/locales`, `/voices`, `/process`) already sit at root level.

Changes required:
- Remove `prefix="/api/v1"` from the health router so the route path `/health` resolves at root
- Update all test requests from `/api/v1/health` to `/health`

## Acceptance criteria

- [x] `GET /health` returns `{"status": "ok"}` with 200
- [x] `HEAD /health` returns 200 with no body
- [x] `pytest tests/test_health.py` passes
- [x] No remaining references to `/api/v1/health` in test files

## Blocked by

None - can start immediately
