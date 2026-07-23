---
title: "Add tests for external cancellation of close() on ExponentialDecayCache"
labels:
  - ready-for-agent
created: 2026-07-23
---

Status: ready-for-agent

## What to build

Add two async tests to `tests/test_cache.py::TestKnownBugs` that verify the
emergency `CancelledError` path in `ExponentialDecayCache.close()`:

1. **Happy path** — Items are in the cache when `close()` is externally
   cancelled. Verify that `on_evict` is called at least once via the emergency
   handler and that the evicted items include the ones that were put into the
   cache.

2. **Empty cache negative case** — No items in the cache when `close()` is
   externally cancelled. Verify that `on_evict` is NOT called (the batch is
   empty, so the emergency handler skips the callback).

The tests must NOT access the private `_cleaner_task` attribute. Instead,
cancellation is triggered by spawning `close()` in an `asyncio.Task` and
cancelling that task. Use `pytest.raises(asyncio.CancelledError)` to catch the
re-raised exception.

Use `eviction_interval=3600.0` to make the `_cleaner_worker` sleep, ensuring
`on_evict` can only be invoked through the emergency `CancelledError` path.

## Acceptance criteria

- [x] `test_close_cancelled_externally_calls_on_evict_emergency` exists and
      passes: `on_evict` is called with the evicted items when `close()` is
      externally cancelled
- [x] `test_close_cancelled_externally_empty_cache_no_on_evict` exists and
      passes: `on_evict` is NOT called when `close()` is externally cancelled
      on an empty cache
- [x] All existing cache tests still pass
- [x] No use of `._cleaner_task` in test code

## Blocked by

None — can start immediately.
