---
title: "Extract _resolve_device to module-level function and test fallback through public API"
labels:
  - ready-for-human
created: 2026-05-21
---

## What to build

Move the `_resolve_device` instance method on `SileroTTSEngine` to a private module-level function. The method is a pure function of its input (no `self` usage), making it a natural fit alongside the existing module-level helpers (`_load_config_model`, `_select_sample_rate`, `_tensor_to_wav_bytes`).

Replace the direct unit tests of the private method with end-to-end tests through the public `process()` API that verify device fallback behavior produces valid audio output.

## Acceptance criteria

- [x] `_resolve_device` exists as a module-level function (not an instance method)
- [x] Engine initialization calls module-level `_resolve_device` to set `self._device`
- [x] `TestResolveDevice` class is removed from tests
- [x] `test_process_cuda_unavailable_falls_back_to_cpu` — engine configured with `device="cuda"` with CUDA mocked unavailable falls back to CPU and `process()` returns valid WAV
- [x] `test_process_xpu_unavailable_falls_back_to_cpu` — engine configured with `device="xpu"` with XPU mocked unavailable falls back to CPU and `process()` returns valid WAV
- [x] All tests pass

## Blocked by

None — can start immediately
