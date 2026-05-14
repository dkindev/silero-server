---
title: "Add TTS_CONFIG_PATH and TTS_MAX_CONCURRENT_PER_LOCALE"
labels:
  - ready-for-agent
created: 2026-05-14
---

## What to build

Add two new configuration fields to `src/config.py`:
- `TTS_CONFIG_PATH` — path to voice/locale mapping config file, with validator that checks file exists at startup (fails fast)
- `TTS_MAX_CONCURRENT_PER_LOCALE` — max concurrent requests per locale, constrained to range 1-10

Update `.env.example` to include the missing variable. Update test files accordingly.

## Acceptance criteria

- [x] Settings accepts `TTS_CONFIG_PATH` with default `silero-to-mary-config.yml`
- [x] Settings accepts `TTS_MAX_CONCURRENT_PER_LOCALE` with default `2`
- [x] Invalid `TTS_CONFIG_PATH` (non-existent file) fails at startup with clear error
- [x] Invalid `TTS_MAX_CONCURRENT_PER_LOCALE` (e.g., 0, 11) fails at startup with clear error
- [x] `.env.example` contains `TTS_MAX_CONCURRENT_PER_LOCALE=2`
- [x] test_env_example.py checks all 7 TTS_* variables
- [x] test_config.py has tests for both new fields

## Blocked by

None - can start immediately