---
title: "Add device resolution and _load_model() helper to SileroTTSEngine"
labels:
  - ready-for-agent
created: 2026-05-18
---

## What to build

Add device resolution and `_load_model()` helper to `SileroTTSEngine`.

**`src/config.py`:**
- Add `device_must_be_valid` field validator for `TTS_DEVICE` accepting `cpu`, `cuda`, `xpu` (case-insensitive)
- Update docstring to reflect supported values

**`src/tts/silero_tts_engine.py`:**
- Add `_resolve_device(device_str)` method checking runtime availability:
  - `cuda` → `torch.cuda.is_available()`, fallback to `cpu`
  - `xpu` → `torch.xpu.is_available()`, fallback to `cpu`
  - `cpu` → use directly
- Store `self._device` in `__init__`
- Add `_load_model(model_name, model_info)` helper:
  - Extract model loading from `process()` (torch.hub.load)
  - Call `model.to(self._device)` in try/except → raise `TTSProcessingError` on failure
  - Cache model and semaphore on success
- Update `process()` to use `self._models.get(model_name) or self._load_model(...)`

**`CONTEXT.md`:**
- Update `TTS_DEVICE` row to reflect `cuda`/`xpu` support and runtime fallback behavior

**`tests/test_silero_tts_engine.py`:**
- Test `_resolve_device`: `cuda` unavailable → `cpu`; `xpu` unavailable → `cpu`
- Test `_load_model`: `model.to()` raises → `TTSProcessingError`, model not cached; success → model cached and on correct device

## Acceptance criteria

- [x] `TTS_DEVICE=cuda` falls back to `cpu` when GPU unavailable
- [x] `TTS_DEVICE=xpu` falls back to `cpu` when XPU unavailable
- [x] `model.to(device)` raises → `TTSProcessingError`, model not cached
- [x] Model cached and moved to correct device on success
- [x] `TTS_DEVICE` validator rejects invalid values