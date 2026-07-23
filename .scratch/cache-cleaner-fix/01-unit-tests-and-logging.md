---
title: "01 - Unit tests + logging for ExponentialDecayCache"
labels:
  - ready-for-agent
created: 2026-07-23
---

## What to build

Add a `tests/test_cache.py` file with focused unit tests for `ExponentialDecayCache`: `put`, `get`, `__len__`, `_decay_score`, `_update_score`, `_evict_lowest_element`, `clear`, `close`, and cleaner lifecycle. Tests should document expected behavior including the known bugs (marked as expected failures with references to the fix issues).

Also add `from loguru import logger` to `cache.py` and replace the silent `except Exception:` block in `_cleaner_worker` with a `logger.exception()` call so eviction failures are visible instead of swallowed.

## Acceptance criteria

- [x] `tests/test_cache.py` exists with tests covering all public methods of `ExponentialDecayCache`
- [x] Cleaner worker logs exceptions from `on_evict` instead of swallowing them
- [x] All existing tests still pass (`pytest tests/`)
- [x] Known-bug tests are present documenting:
- [x] Double `task_done()` crash in `_cleaner_worker` on shutdown
- [x] Missing `await` in `close()` — `clear()` not called
- [x] `None` sentinel incorrectly passed to `on_evict` batch

## Blocked by

None — can start immediately.
