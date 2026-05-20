---
title: "Make select_sample_rate private"
labels:
  - needs-triage
created: 2026-05-20
---

## What to build

Refactor `select_sample_rate` to be a private module-level function by renaming it to `_select_sample_rate`. Remove the tests for this public API since it's now internal implementation.

## Acceptance criteria

- [ ] `select_sample_rate` renamed to `_select_sample_rate` in `src/tts/silero_tts_engine.py`
- [ ] Internal call site updated to use `_select_sample_rate`
- [ ] `TestSelectSampleRate` class removed from test file

## Blocked by

None - can start immediately