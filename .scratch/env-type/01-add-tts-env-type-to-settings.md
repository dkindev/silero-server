---
title: "Add TTS_ENV_TYPE environment variable to Settings with validation"
labels:
  - ready-for-agent
created: 2026-06-07
---

## What to build

Add a new `TTS_ENV_TYPE` environment variable to the `Settings` model in `src/config.py`.

- Field name: `TTS_ENV_TYPE`
- Type: `Literal["development", "production"]`
- Default: `"development"`
- Prefix: `TTS_` (consistent with all other settings)

Invalid values (anything other than `"development"` or `"production"`) raise `ValidationError` at startup.

Update `.env.example` with an example entry and `CONTEXT.md` with a row in the configuration table.

## Acceptance criteria

- [x] `TTS_ENV_TYPE` field exists on `Settings` with default `"development"`
- [x] `TTS_ENV_TYPE=production` is accepted
- [x] `TTS_ENV_TYPE=invalid` raises `ValidationError` at startup (tested)
- [x] `.env.example` includes `TTS_ENV_TYPE=development`
- [x] `CONTEXT.md` config table documents `TTS_ENV_TYPE` with default and purpose
- [x] `test_env_example.py` includes `TTS_ENV_TYPE` in the required vars list
- [x] Existing tests pass unchanged

## Blocked by

None — can start immediately.
