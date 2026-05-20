---
title: "Move select_sample_rate() to silero_tts_engine.py"
labels:
  - ready-for-agent
created: 2026-05-20
---

## What to build

Move the `select_sample_rate` function from `models.py` to `silero_tts_engine.py`. This keeps `models.py` as a data-classes-only module per project conventions.

- Move function definition from `src/tts/models.py` (lines 61-86) to `src/tts/silero_tts_engine.py`
- Remove `select_sample_rate` from the import statement in `silero_tts_engine.py` (line 14)
- Update test imports in `tests/test_silero_tts_engine.py` to import from `src.tts.silero_tts_engine` instead of `src.tts.models`
- Delete function from `models.py`

## Acceptance criteria

- [x] `select_sample_rate` defined in `silero_tts_engine.py`
- [x] `models.py` contains only dataclasses
- [x] All tests pass with updated imports

## Blocked by

None - can start immediately