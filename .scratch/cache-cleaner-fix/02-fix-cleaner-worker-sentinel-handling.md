---
title: "02 - Fix _cleaner_worker sentinel handling"
labels:
  - ready-for-agent
created: 2026-07-23
---

## What to build

Fix the shutdown logic in `ExponentialDecayCache._cleaner_worker` in `src/tts/cache.py`:

- Stop adding the `None` sentinel to the eviction batch — the `on_evict` callback should never receive `None` as a batch item
- Call `task_done()` exactly once for the sentinel (currently called twice: once in the `if first_item is None` branch and once in the `finally` block, which raises `ValueError`)
- The `finally` block should only call `task_done()` for real eviction items, not for the sentinel

This ensures `close()` completes without crashing and `on_evict` never sees invalid data.

## Acceptance criteria

- [x] `close()` no longer raises `ValueError` from double `task_done()`
- [x] `on_evict` is never called with `None` in the batch list
- [x] The previously-failing bug-documentation tests from issue 01 now pass
- [x] All existing tests still pass (`pytest tests/`)

## Blocked by

- #01 — Unit tests + logging for ExponentialDecayCache (the bug-documentation tests verify the fix)
