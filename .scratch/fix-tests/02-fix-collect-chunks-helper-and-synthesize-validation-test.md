---
title: "Fix collect_chunks helper and synthesize-validation test"
labels:
  - ready-for-agent
created: 2026-06-22
---

## What to build

The `collect_chunks` test helper passes a plain string `"TEXT"` as `text_format`, but `synthesize_pcm_chunks` validates against the `TextFormat` enum — so every valid-synthesis test raises `TTSEngineError("Invalid text format: TEXT")`.

Change `collect_chunks` to default `input_type=TextFormat.TEXT` (the proper enum member). Also update `test_synthesize_invalid_input_type_raises_error` to call `engine.synthesize_pcm_chunks(...)` directly with a raw string `"INVALID"` instead of routing through `collect_chunks`.

## Acceptance criteria

- [x] All 16 tests in `TestSynthesizeValidation` pass
- [x] `test_synthesize_invalid_input_type_raises_error` correctly catches invalid string input
- [x] No other tests are broken

## Blocked by

None — can start immediately.
