---
title: "Add CachedModel wrapper class"
labels:
  - ready-for-agent
created: 2026-05-19
---

## What to build

Add a `CachedModel` dataclass in `silero_tts_engine.py` that bundles together:
- `model: Any` — the loaded Silero model
- `sample_rate: int` — the selected sample rate for this model
- `semaphore: asyncio.Semaphore` — concurrency control for this model

This enables caching sample_rate alongside the model at load time rather than computing it per-request.

## Acceptance criteria

- [x] CachedModel dataclass exists in silero_tts_engine.py
- [x] Fields include model, sample_rate, and semaphore with correct types
- [x] CachedModel is used by the engine class

## Blocked by

None - can start immediately