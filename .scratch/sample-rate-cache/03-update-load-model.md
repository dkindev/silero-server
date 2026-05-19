---
title: "Update _load_model to use CachedModel"
labels:
  - ready-for-agent
created: 2026-05-19
---

## What to build

Modify `_load_model` in `SileroTTSEngine` to:
1. Call the moved `select_sample_rate` function to determine sample_rate at load time
2. Create a `CachedModel` instance with model, sample_rate, and semaphore
3. Store the CachedModel in `self._models` dict
4. Return the CachedModel wrapper

## Acceptance criteria

- [x] _load_model calls select_sample_rate from models.py
- [x] Returns CachedModel instead of raw model
- [x] Sample rate is selected once at model load time
- [x] Semaphore is included in CachedModel

## Blocked by

- 02-move-sample-rate-function