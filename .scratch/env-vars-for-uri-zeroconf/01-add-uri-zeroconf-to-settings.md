---
title: "Add TTS_URI and TTS_ZEROCONF to Settings"
labels:
  - ready-for-agent
created: 2026-06-18
---

## What to build

Add `TTS_URI` (default `"tcp://0.0.0.0:10200"`) and `TTS_ZEROCONF` (default `""`, disabled) to the Pydantic `Settings` class in `config.py`. Update `.env.example` and `.env` with both new variables. The CLI in `main.py` is unchanged — `--uri`/`--zeroconf` still work.

## Acceptance criteria

- [x] `Settings` has `TTS_URI: str = "tcp://0.0.0.0:10200"`
- [x] `Settings` has `TTS_ZEROCONF: str = ""`
- [x] `TTS_ZEROCONF` being unset or empty means zeroconf disabled
- [x] Setting env vars overrides defaults in `get_settings()`
- [x] `.env.example` contains both new vars with example values
- [x] `.env` contains both new vars with example values
- [x] Server startup behavior is unchanged (CLI still drives `--uri`/`--zeroconf`)

## Blocked by

None - can start immediately
