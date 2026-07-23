---
title: "01 - Add is_closed property + idempotent close() to ExponentialDecayCache"
labels:
  - ready-for-agent
created: 2026-07-23
---

## What to build

Add a `is_closed` property to `ExponentialDecayCache` and make `close()` idempotent so tests no longer need private member access (`_cleaner_task`, `_eviction_queue`) for lifecycle management.

Specifically, in `src/tts/cache.py`:

- Add `self._closed = False` in `__init__`
- Add a `is_closed` property that returns `self._closed`
- Make `close()` idempotent: if already closed, return immediately. Otherwise set `self._closed = True` at the start, then proceed with `await self.clear()`, sentinel, and `await self._cleaner_task`

In `tests/test_cache.py`:

- Remove the `_cleanup_cache` helper function (which accessed `c._cleaner_task` directly)
- Replace all fixture teardowns and test-finally blocks with `await cache.close()` (safe because `close()` is now idempotent)
- `test_close_terminates_cleaner_task` uses `cache.is_closed` instead of `cache._cleaner_task.done()`
- `test_no_double_task_done_on_shutdown` uses `await c.close()` + `assert c.is_closed` instead of try/except + _cleanup_cache
- `test_none_sentinel_not_passed_to_on_evict` uses `await c.close()` without try/except wrapper

## Acceptance criteria

- [x] `ExponentialDecayCache` has a public `is_closed` property (bool)
- [x] `close()` is idempotent — calling it twice does not raise
- [x] `_cleanup_cache` helper is removed — all teardown uses `close()`
- [x] No test accesses `_cleaner_task` directly
- [x] All existing tests still pass (`pytest tests/`)

## Blocked by

None — can start immediately.