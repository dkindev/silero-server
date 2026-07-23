---
title: "02 - Rewrite eviction-callback tests without _eviction_queue access"
labels:
  - ready-for-agent
created: 2026-07-23
---

## What to build

Remove direct access to the private `_eviction_queue` from two `on_evict` callback tests and delete one test that only existed to check queue state.

In `tests/test_cache.py`:

- **`test_on_evict_called_with_evicted_item`**: Replace `await c._eviction_queue.join()` with `await c.close()`. Instead of `on_evict.assert_called_once()`, scan `on_evict.call_args_list` to verify `("a", 1)` was among the evicted items. The `close()` call enqueues the remaining item too, so `called_once` is no longer the right assertion — but the important check is that the evicted key-value pair reached the callback.

- **`test_on_evict_called_with_cleared_items`**: Replace `await c._eviction_queue.join()` with `await c.close()`. The test already scans `call_args_list`, so no assertion change needed.

- **Remove `test_clear_pushes_to_eviction_queue`**: This test only existed to check `cache._eviction_queue.empty()` — it is already covered by `test_clear_removes_all_items` (len check) and `test_on_evict_called_with_cleared_items` (callback check).

## Acceptance criteria

- [x] `test_on_evict_called_with_evicted_item` verifies evicted items reached `on_evict` without accessing `_eviction_queue`
- [x] `test_on_evict_called_with_cleared_items` verifies cleared items reached `on_evict` without accessing `_eviction_queue`
- [x] `test_clear_pushes_to_eviction_queue` is removed
- [x] No test accesses `_eviction_queue` directly
- [x] All tests still pass (`pytest tests/`)

## Blocked by

- #01 — Add is_closed property + idempotent close() to ExponentialDecayCache