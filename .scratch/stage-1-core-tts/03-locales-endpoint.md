---
title: "Stage 1: GET /api/v1/locales Endpoint"
labels:
  - ready-for-agent
created: 2026-05-12
---

## Parent

docs/stages/1.md

## What to build

Create `src/routers/locales.py` — GET /api/v1/locales endpoint.

- Returns available locales as plain text, one per line (e.g., `ru_RU\nde_DE\n`).
- Reuses `get_available_locales()` from src/silero.py.
- Lazy discovery: parse cached models on first call, cache in memory.
- Returns 200 OK with Content-Type: text/plain.
- Returns empty body if no models are cached.

## Acceptance criteria

- [ ] GET /api/v1/locales returns 200 OK
- [ ] Content-Type: text/plain
- [ ] One locale per line in Mary-TTS format (ru_RU, not ru)
- [ ] Empty body when no models cached
- [ ] Lazy discovery (first call parses, subsequent calls use cache)

## Blocked by

- Stage 1: Silero Wrapper Module