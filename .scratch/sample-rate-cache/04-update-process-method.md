---
title: "Update process method to use CachedModel"
labels:
  - ready-for-agent
created: 2026-05-19
---

## What to build

Update the `process` method in `SileroTTSEngine` to extract model, sample_rate, and semaphore from the `CachedModel` wrapper instead of calling `_select_sample_rate` per-request.

The model retrieval from cache should now return a CachedModel, and the code should:
1. Extract `.model` for the TTS call
2. Use `.sample_rate` directly (no selection logic)
3. Use `.semaphore` for concurrency control

## Acceptance criteria

- [x] process extracts model, sample_rate, semaphore from CachedModel
- [x] No per-request _select_sample_rate call
- [x] TTS call uses cached sample_rate
- [x] Functionality unchanged from user perspective

## Blocked by

- 03-update-load-model