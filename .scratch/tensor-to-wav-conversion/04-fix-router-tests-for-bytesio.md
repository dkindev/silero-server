---
title: "Fix router-layer tests for BytesIO streaming"
labels:
  - ready-for-agent
created: 2026-05-22
---

## Parent

`.scratch/tensor-to-wav-conversion/03-fix-engine-tests-for-bytesio.md`

## What to build

The `/process` endpoint now passes `TTSResult.audio` (an `io.BytesIO` instance) to `StreamingResponse(content=result.audio, ...)`. Four router tests mock `TTSResult` with raw `bytes` as the audio payload, which crashes in Starlette 1.0.0 (`StreamingResponse` tries to iterate `bytes` → yields `int` → `AttributeError`).

Tests affected:
- `TestProcessEndpoint::test_process_returns_wav`
- `TestProcessEndpoint::test_process_returns_content_disposition_inline`
- `TestProcessPostEndpoint::test_post_process_returns_wav`
- `TestProcessPostEndpoint::test_post_process_returns_audio_wav_content_type`

Update each mock payload from raw `bytes` to `io.BytesIO(...)`:

```python
# before
mock_result = TTSResult(audio=b"RIFF" + b"\x00" * 555, ...)

# after
import io
mock_result = TTSResult(audio=io.BytesIO(b"RIFF" + b"\x00" * 555), ...)
```

## Acceptance criteria

- [x] All 4 router tests pass with `BytesIO` mock payloads
- [x] `pytest tests/test_routers.py` exits 0
- [x] `curl /process` still returns a valid WAV file

## Blocked by

- `.scratch/tensor-to-wav-conversion/03-fix-engine-tests-for-bytesio.md`
