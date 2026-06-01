---
title: "Fix mock setup in router tests (5 failing tests)"
labels:
  - ready-for-agent
created: 2026-06-01
---

## What to build

Two independent mock-chain bugs in `tests/test_routers.py` cause 5 tests to fail:

1. **`test_locales_returns_one_per_line`** — sets `mock_engine.get_locales.return_value` but the production code calls `engine.get_storage().get_locales()`. The mock bypasses `get_storage()` entirely, returning empty string instead of `"ru_RU\nde_DE\nen_US"`.

2. **Four process endpoint tests** (`test_process_returns_wav`, `test_process_returns_content_disposition_inline`, `test_post_process_returns_wav`, `test_post_process_returns_audio_wav_content_type`) use `AsyncMock()` as the engine mock. On an `AsyncMock`, every attribute access yields an `AsyncMock`, so `engine.get_storage()` returns a coroutine instead of a sync mock. At runtime this gives `AttributeError: 'coroutine' object has no attribute 'has_locale'`. Fix: replace `AsyncMock()` with `MagicMock()` for the engine and set `mock_engine.process = AsyncMock()` to keep the async method async.

## Acceptance criteria

- [x] `test_locales_returns_one_per_line` passes
- [x] `test_process_returns_wav` passes
- [x] `test_process_returns_content_disposition_inline` passes
- [x] `test_post_process_returns_wav` passes
- [x] `test_post_process_returns_audio_wav_content_type` passes
- [x] All 118 tests pass with no regressions

## Blocked by

None - can start immediately
