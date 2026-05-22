---
title: "Fix engine-layer tests for BytesIO return type"
labels:
  - ready-for-agent
created: 2026-05-22
---

## What to build

`_tensor_to_wav_bytes()` now returns `io.BytesIO` instead of `bytes`, and `TTSResult.audio` is typed as `io.BytesIO`. Six engine-layer tests assert the old `bytes` contract and fail:

- `TestProcessValidation::test_process_successful_synthesis_returns_tts_result`
- `TestProcessValidation::test_process_converts_tensor_to_wav_bytes`
- `TestProcessValidation::test_process_cuda_unavailable_falls_back_to_cpu`
- `TestProcessValidation::test_process_xpu_unavailable_falls_back_to_cpu`
- `TestProcessWithProvider::test_process_uses_provider_for_model_path`

All five check `isinstance(result.audio, bytes)` and call `result.audio.startswith(b"RIFF")` — neither works on `io.BytesIO`.

Update each assertion to:
- `isinstance(result.audio, io.BytesIO)` instead of `isinstance(result.audio, bytes)`
- `result.audio.read().startswith(b"RIFF")` instead of `result.audio.startswith(b"RIFF")`
- `result.audio.seek(0)` before re-reading where a test needs the buffer again

## Acceptance criteria

- [x] All 6 engine-layer tests pass with `BytesIO` assertions
- [x] Existing test for `test_process_converts_tensor_to_wav_bytes` still validates actual WAV bytes round-trip
- [x] `pytest tests/test_silero_tts_engine.py tests/test_engine_factory.py` exits 0

## Blocked by

None — can start immediately
