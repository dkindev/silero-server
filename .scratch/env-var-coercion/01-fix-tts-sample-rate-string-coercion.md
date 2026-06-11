---
title: "Fix TTS_SAMPLE_RATE env var string-to-int coercion"
labels:
  - ready-for-agent
created: 2026-06-11
---

## What to build

`pydantic-settings` reads environment variables as strings. The `TTS_SAMPLE_RATE` field is typed `Literal[8000, 16000, 22050, 24000, 48000]`, and pydantic v2's `Literal` validator enforces strict equality — `'48000' != 48000` — so `Settings()` fails at startup when loaded from `.env`.

Add a `mode="before"` field validator that converts string inputs to `int` before the `Literal` check. Add a test that verifies string input (simulating env var loading) works correctly.

## Acceptance criteria

- [x] `cp .env.example .env && python -c "from src.config import get_settings; s=get_settings(); print(s.TTS_SAMPLE_RATE)"` prints `48000` without error
- [x] `Settings.model_validate({"TTS_SAMPLE_RATE": "48000"})` passes and `settings.TTS_SAMPLE_RATE == 48000`
- [x] Existing `pytest tests/test_config.py` suite still passes
- [x] No other env var fields affected by the change

## Blocked by

None - can start immediately
