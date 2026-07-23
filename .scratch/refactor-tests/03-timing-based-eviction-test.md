---
title: "03 - Replace TestInternals with timing-based eviction test"
labels:
  - ready-for-agent
created: 2026-07-23
---

## What to build

Remove the `TestInternals` test class which tests private methods (`_decay_score`, `_update_score`, `_evict_lowest_element`) and private fields (`_meta`, `_cache`, `_eviction_queue`) directly. Replace it with a single timing-based integration test that verifies eviction behavior through the public API only.

Remove these five tests from `tests/test_cache.py`:

- `test_decay_score_zero_delta` — called `cache._decay_score()` with `cache._meta["a"]["last_updated"]`
- `test_decay_score_positive_delta` — called `cache._decay_score()` with `cache._meta["a"]["last_updated"] + 10`
- `test_update_score_adds_one` — called `cache._update_score()` with `cache._meta["a"]["last_updated"] + 10`
- `test_evict_lowest_element_removes_lowest_score` — called `cache._evict_lowest_element()` with manual timestamp, checked `cache._cache` dict
- `test_evict_lowest_element_adds_to_eviction_queue` — called `cache._evict_lowest_element()`, checked `cache._eviction_queue.empty()`

Replace with a new class `TestScoreEviction` containing one test `test_eviction_order_by_score`:

```
capacity=2, half_life_seconds=1
put("a", 1)           → score=1.0 at T0
wait 1 second          → "a" decays to ~0.5
put("b", 2)            → score=1.0 at T0+1
get("a")               → decays "a" from ~0.5, adds 1.0 → score=~1.5; "b" unchanged
put("c", 3)            → evicts lowest scored: "b" (score ~1.0) < "a" (~1.5)
assert get("b") is None   → "b" was evicted
assert get("a") == 1      → "a" survives
assert len(cache) == 2    → capacity maintained
```

This verifies that decay scoring + eviction work together correctly through the public `put()`/`get()`/`len()` API, without exposing implementation internals.

## Acceptance criteria

- [x] `TestInternals` class is removed
- [x] `TestScoreEviction.test_eviction_order_by_score` exists and passes
- [x] Eviction order is verified solely through public API (`put()`, `get()`, `len()`)
- [x] All tests still pass (`pytest tests/`)

## Blocked by

- #01 — Add is_closed property + idempotent close() to ExponentialDecayCache