---
title: "02: Rename test file test_silero_tts_engine.py -> test_engine.py"
labels:
  - ready-for-agent
created: 2026-06-04
---

## Parent

Conversation with agent on 2026-06-04: rename silero_tts_engine.py to engine.py for readability.

## What to build

Rename `tests/test_silero_tts_engine.py` to `tests/test_engine.py` to match the renamed source module. No content changes needed — imports were already updated in the previous slice.

## Acceptance criteria

- [x] `tests/test_silero_tts_engine.py` is renamed to `tests/test_engine.py`
- [x] `pytest` discovers and runs all engine tests from the new filename
- [x] All tests pass

## Blocked by

- `.scratch/rename-engine-module/01-rename-source-module.md`
