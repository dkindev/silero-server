---
title: "Rename TTS_DEVICE → TTS_TORCH_DEVICE"
labels:
  - ready-for-agent
created: 2026-05-25
---

## What to build

Rename the `TTS_DEVICE` environment variable to `TTS_TORCH_DEVICE` for consistency with the new `TTS_TORCH_*` naming scheme.

Update the `Settings` field name and validator error message in `src/config.py`, the wiring in `src/main.py`, `.env.example`, `CONTEXT.md`, `README.md`, and all test references. The internal `TTSConfig.device` Python dataclass field stays as-is — only the user-facing env var changes.

This is a breaking change: anyone with `TTS_DEVICE` set in their environment will silently fall back to the `cpu` default until they update to `TTS_TORCH_DEVICE`.

## Changes

| File | Change |
|------|--------|
| `src/config.py` | Rename `TTS_DEVICE: str = "cpu"` → `TTS_TORCH_DEVICE: str = "cpu"`; update `field_validator("TTS_DEVICE")` → `field_validator("TTS_TORCH_DEVICE")`; update error message string `"Invalid TTS_DEVICE"` → `"Invalid TTS_TORCH_DEVICE"` |
| `src/main.py` | `app_settings.TTS_DEVICE` → `app_settings.TTS_TORCH_DEVICE` |
| `.env.example` | `TTS_DEVICE=cpu` → `TTS_TORCH_DEVICE=cpu` |
| `CONTEXT.md` | Update line 61 (`TTS_DEVICE` → `TTS_TORCH_DEVICE`), line 132 (config table row) |
| `README.md` | Update env vars table (line 65) |
| `tests/test_config.py` | Update all `TTS_DEVICE` → `TTS_TORCH_DEVICE` in field names, test names, `hasattr` checks, and `model_validate` dict keys |
| `tests/test_env_example.py` | Update `TTS_DEVICE` → `TTS_TORCH_DEVICE` in required vars list |

## Acceptance criteria

- [x] `TTS_DEVICE=cuda` in `.env` is silently ignored; app defaults to `cpu`
- [x] `TTS_TORCH_DEVICE=cuda` works (falls back to `cpu` if GPU unavailable)
- [x] `TTS_TORCH_DEVICE=vulkan` raises `ValidationError` at startup
- [x] All existing tests pass with updated field names
- [x] `.env.example`, `CONTEXT.md`, and `README.md` reflect the new name

## Blocked by

None — can start immediately.
