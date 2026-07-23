---
title: "03 - Fix close() to await clear()"
labels:
  - ready-for-agent
created: 2026-07-23
---

## What to build

Fix `ExponentialDecayCache.close()` in `src/tts/cache.py` to actually execute the `clear()` coroutine. Currently `self.clear()` is called without `await`, so the coroutine is created but never executed — cached items are never enqueued for eviction, and model resources (including GPU memory) are leaked on shutdown.

Change `self.clear()` to `await self.clear()`.

## Acceptance criteria

- [x] `close()` calls `clear()` (the coroutine is awaited, not just created)
- [x] All cached items are passed to `on_evict` during shutdown
- [x] Dicts `_cache` and `_meta` are empty after `close()`
- [x] The previously-failing bug-documentation tests from issue 01 now pass
- [x] All existing tests still pass (`pytest tests/`)

## Blocked by

- #02 — Fix _cleaner_worker sentinel handling (`close()` crashes with `ValueError` before issue 02's fix)
