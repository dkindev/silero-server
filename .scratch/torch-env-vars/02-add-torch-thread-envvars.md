---
title: "Add TTS_TORCH_NUM_THREADS, TTS_TORCH_NUM_INTEROP_THREADS, TTS_TORCH_FLUSH_DENORMAL"
labels:
  - ready-for-agent
created: 2026-05-25
---

## What to build

Add three new environment variables to control PyTorch threading and performance knobs at startup, replacing hardcoded values in the app lifespan:

| Variable | Type | Default | Validation |
|---|---|---|---|
| `TTS_TORCH_NUM_THREADS` | int | `4` | `ge=1` |
| `TTS_TORCH_NUM_INTEROP_THREADS` | int | `1` | `ge=1` |
| `TTS_TORCH_FLUSH_DENORMAL` | bool | `true` | — |

- `TTS_TORCH_NUM_THREADS` → `torch.set_num_threads()`
- `TTS_TORCH_NUM_INTEROP_THREADS` → `torch.set_num_interop_threads()`
- `TTS_TORCH_FLUSH_DENORMAL` → `torch.set_flush_denormal(True)`, gated by `hasattr(torch, 'set_flush_denormal')` guard. When `false`, the call is skipped entirely.

Add to `Settings`, wire into the lifespan in `main.py`, document in `.env.example` and `CONTEXT.md`, and test defaults/validation in `tests/test_config.py`.

## Changes

| File | Change |
|------|--------|
| `src/config.py` | Add 3 fields to `Settings` class |
| `src/main.py` | Replace hardcoded `torch.set_num_threads(2)` / `torch.set_num_interop_threads(1)` / `torch.set_flush_denormal(True)` with `app_settings.*` reads |
| `.env.example` | Add 3 new entries |
| `CONTEXT.md` | Add 3 rows to config table |
| `tests/test_config.py` | Add tests for defaults, validation bounds, and behavior |

## Acceptance criteria

- [x] Defaults: `TTS_TORCH_NUM_THREADS=4`, `TTS_TORCH_NUM_INTEROP_THREADS=1`, `TTS_TORCH_FLUSH_DENORMAL=true`
- [x] `TTS_TORCH_NUM_THREADS=0` and negative values raise `ValidationError` at startup
- [x] `TTS_TORCH_NUM_INTEROP_THREADS=0` and negative values raise `ValidationError` at startup
- [x] `TTS_TORCH_FLUSH_DENORMAL=false` skips the flush call entirely (even if the function exists)
- [x] `TTS_TORCH_FLUSH_DENORMAL=true` only calls `torch.set_flush_denormal(True)` when `hasattr(torch, 'set_flush_denormal')` passes
- [x] `.env.example` and `CONTEXT.md` document all three vars
- [x] Existing tests pass unchanged (purely additive change)

## Blocked by

None — can start immediately.
