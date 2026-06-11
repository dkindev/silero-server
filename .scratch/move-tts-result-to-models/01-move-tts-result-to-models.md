---
title: "Move TTSResult to models.py and make frozen"
labels:
  - ready-for-agent
created: 2026-06-11
---

## What to build

Move the `TTSResult` dataclass from `src/tts/result.py` into `src/tts/models.py`, making it `frozen=True` for consistency with the other dataclasses in that file (all existing dataclasses in `models.py` are frozen). Update all imports across production and test code. Remove the now-empty `result.py` file. Delete the `test_tts_result_is_mutable` test in `test_tts_models.py` since frozen dataclasses are not mutable. No functional changes — `TTSResult` is never mutated in production code.

## Acceptance criteria

- [x] `TTSResult` is defined in `src/tts/models.py` as a frozen dataclass with fields `audio: io.BytesIO`, `sample_rate: int`, `model: str`
- [x] All imports of `TTSResult` across the codebase reference `src.tts.models` instead of `src.tts.result`
- [x] `src/tts/result.py` is deleted
- [x] The `test_tts_result_is_mutable` test is removed
- [x] All existing tests pass

## Blocked by

None — can start immediately
