---
title: "Tensor-to-WAV conversion in SileroTTSEngine.process()"
labels:
  - ready-for-agent
created: 2026-05-21
completed: 2026-05-21
---

## What to build

`model.apply_tts()` returns a PyTorch tensor of raw audio samples, but the engine currently passes it directly as `TTSResult(audio=audio, ...)` where `audio` is typed as `bytes`. This is a type mismatch hidden by tests that mock `apply_tts` to return fake WAV bytes.

Add a module-level helper `_tensor_to_wav_bytes(audio, sample_rate) → bytes` in `silero_tts_engine.py` that:

1. Normalizes 1D tensors to 2D `[1, T]` via `unsqueeze(0)`
2. Saves 16-bit PCM WAV to an in-memory buffer using `torchaudio.save(uri=buffer, src=audio.cpu(), sample_rate=sample_rate, format="wav", bits_per_sample=16)`
3. Returns the buffer bytes
4. Wraps any exception in `TTSEngineError("Failed to convert tensor to WAV: {e}")`

Wire the helper into `process()`: call it on the output of `apply_tts` before constructing `TTSResult`.

## Acceptance criteria

- [x] `_tensor_to_wav_bytes(torch.zeros(1, 48000), 48000)` returns bytes starting with `b"RIFF"`
- [x] `_tensor_to_wav_bytes(torch.zeros(48000), 48000)` (1D input) also returns valid WAV bytes
- [x] `process()` returns `TTSResult(audio=<valid WAV bytes>, ...)` for valid inputs
- [x] `_tensor_to_wav_bytes` raises `TTSEngineError` on failure (e.g., empty tensor)
- [x] `import io` and `import torchaudio` added at top of `silero_tts_engine.py`
- [x] Existing orchestration tests updated: `apply_tts` mocked to return a tensor, `_tensor_to_wav_bytes` mocked to return fake WAV bytes
- [x] Dedicated unit-test class `TestTensorToWavBytes` added with real tensor → WAV round-trip
- [x] All existing tests still pass

## Blocked by

None — can start immediately
