---
title: "Add TTS_MODELS_DIR to .env.example, test, and README"
labels:
  - ready-for-agent
created: 2026-06-04
---

## What to build

`TTS_MODELS_DIR` is defined in the `Settings` class (`src/config.py`), consumed in `src/deps.py`, and documented in `CONTEXT.md` — but it is missing from `.env.example`, the test that validates `.env.example` contains all env vars, and the `README.md` env vars table.

Add `TTS_MODELS_DIR` to all three locations so that its example value, test coverage, and user-facing documentation are complete.

## Acceptance criteria

- [x] `.env.example` contains `TTS_MODELS_DIR=.models/silero`
- [x] `test_env_example.py` checks `TTS_MODELS_DIR` in the required vars list
- [x] `README.md` env vars table lists all 12 `TTS_*` variables with defaults and descriptions (currently only lists `TTS_TORCH_DEVICE`)
- [x] `pytest tests/test_env_example.py` passes
- [x] `ruff check` passes

## Blocked by

None — can start immediately
