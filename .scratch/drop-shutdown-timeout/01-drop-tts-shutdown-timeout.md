---
title: "Drop TTS_SHUTDOWN_TIMEOUT environment variable"
labels:
  - ready-for-agent
created: 2026-06-04
---

## What to build

Remove the `TTS_SHUTDOWN_TIMEOUT` environment variable entirely. It is declared in the `Settings` model but never read by any runtime code — the engine's `shutdown()` has no timeout parameter and there is no custom drain logic. Gunicorn's built-in graceful timeout (default 30s) already handles worker shutdown.

## Changes

| File | Change |
|------|--------|
| `src/config.py` | Remove `TTS_SHUTDOWN_TIMEOUT` field + docstring from `Settings` |
| `.env.example` | Remove `TTS_SHUTDOWN_TIMEOUT=10` line |
| `tests/test_config.py` | Remove `test_settings_shutdown_timeout_default`, `test_invalid_shutdown_timeout_zero_fails`, `test_invalid_shutdown_timeout_negative_fails`, `test_valid_shutdown_timeout`; remove `"TTS_SHUTDOWN_TIMEOUT"` from `test_settings_has_all_tts_fields` `hasattr` list |
| `tests/test_env_example.py` | Remove `"TTS_SHUTDOWN_TIMEOUT"` from required vars list |
| `README.md` | Remove `TTS_SHUTDOWN_TIMEOUT` row from env vars table |
| `CONTEXT.md` | Remove `TTS_SHUTDOWN_TIMEOUT` row from config table; rephrase graceful shutdown description to remove env var reference |
| `.scratch/config/01-config.md` | Remove 3 lines referencing `TTS_SHUTDOWN_TIMEOUT` |

## Acceptance criteria

- [x] `git grep TTS_SHUTDOWN_TIMEOUT` returns empty
- [x] `pytest tests/` passes
- [x] `Settings` model validates cleanly with no unknown-field errors for existing env files (backward compat — removing a field is a breaking change only if someone was setting it; the app continues to work for anyone who was setting it, since Pydantic ignores extra fields by default)

## Blocked by

None — can start immediately.
