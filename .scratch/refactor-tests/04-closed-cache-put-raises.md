---
title: "04 - Raise RuntimeError from put() when cache is closed"
labels:
  - ready-for-agent
created: 2026-07-23
---

## What to build

Enforce the invariant that an `ExponentialDecayCache` is single-use: after `close()`, calling `put()` must fail immediately rather than silently writing to a shutting-down data structure.

In `src/tts/cache.py`:

- Add a `self.is_closed` check at the top of `put()`, before the capacity check. If closed, raise `RuntimeError("cache is closed")`.

In `tests/test_cache.py`:

- Add `test_put_on_closed_cache_raises`: create a cache, put one item, close it, then verify `put()` raises `RuntimeError`. Also verify the cache was not modified (len unchanged).

## Acceptance criteria

- [x] `put()` raises `RuntimeError("cache is closed")` when called on a closed cache
- [x] `put()` on a fresh (non-closed) cache still works normally
- [x] `test_put_on_closed_cache_raises` exists and passes
- [x] All tests still pass (`pytest tests/`)

## Blocked by

- #01 — Add is_closed property + idempotent close() to ExponentialDecayCache