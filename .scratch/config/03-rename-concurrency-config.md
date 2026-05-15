---
title: "Rename TTS_MAX_CONCURRENT_PER_LOCALE to TTS_MAX_CONCURRENT_PER_MODEL"
labels:
  - ready-for-human
created: 2026-05-15
---

## What to build

Rename the concurrency configuration from per-locale to per-model to match the actual implementation. The engine uses per-model semaphores, not per-locale, so the naming was misleading.

Changes required:
- Environment variable: `TTS_MAX_CONCURRENT_PER_LOCALE` → `TTS_MAX_CONCURRENT_PER_MODEL`
- Python attribute: `max_concurrent_per_locale` → `max_concurrent_per_model`
- Update all references in config, models, engine, tests, and documentation

## Acceptance criteria

- [x] `TTS_MAX_CONCURRENT_PER_MODEL` env var accepted with same constraints (1-10, default 2)
- [x] `TTSConfig.max_concurrent_per_model` attribute exists with same validation
- [x] Engine uses `max_concurrent_per_model` for per-model semaphore limits
- [x] All tests pass after rename
- [x] Documentation reflects new naming

## Blocked by

None - can start immediately