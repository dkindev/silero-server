---
title: "Device-aware tensor-to-WAV conversion"
labels:
  - ready-for-agent
created: 2026-05-21
completed: 2026-05-21
---

## Parent

`.scratch/tensor-to-wav-conversion/01-tensor-to-wav-conversion.md`

## What to build

`_tensor_to_wav_bytes()` currently always converts on CPU via scipy/numpy, even when the model is on CUDA or XPU. This forces an unnecessary GPU→CPU transfer on every synthesis.

Refactor `_tensor_to_wav_bytes` to accept a `device` parameter and dispatch to three paths:

- **CPU** — scipy/numpy with `.detach().numpy()`, `np.clip` clipping, int16 PCM
- **CUDA** — `torchcodec.encoders.encode_audio` on GPU, no CPU transfer, `torch.clamp` clipping
- **XPU** — same as CUDA but with `intel_extension_for_pytorch` and `torchcodec_xpu` imported lazily; raises `TTSEngineError` with a clear message if these packages are not installed

All three paths apply clipping (`np.clip` or `torch.clamp` to [-1.0, 1.0]) before scaling to int16 PCM.

Update the call site in `process()` to pass `self._device`.

## Acceptance criteria

- [x] `_tensor_to_wav_bytes` signature changed to `(audio, sample_rate, device)`
- [x] CPU path uses `.detach().numpy()` and `np.clip` (no `.astype(np.float64)`)
- [x] CUDA path uses `torchcodec.encoders.encode_audio` without CPU transfer
- [x] XPU path imports `ipex` and `torchcodec_xpu` lazily, raises `TTSEngineError` if missing
- [x] Clipping applied on all paths before PCM conversion
- [x] Unsupported device types raise `TTSEngineError`
- [x] `process()` passes `self._device` to the helper
- [x] Existing `test_process_converts_tensor_to_wav_bytes` still passes (exercises CPU path)
- [x] All other existing tests still pass

## Blocked by

- `.scratch/tensor-to-wav-conversion/01-tensor-to-wav-conversion.md`
