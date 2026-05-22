---
title: "Update CONTEXT.md for BytesIO return contract"
labels:
  - ready-for-agent
created: 2026-05-22
---

## What to build

`_tensor_to_wav_bytes()` now returns `io.BytesIO` instead of `bytes`, and `TTSResult.audio` is typed as `io.BytesIO`. Reflect these changes in `CONTEXT.md`.

Specific sections to update:

1. **`_tensor_to_wav_bytes`** — change return type from `→ bytes` to `→ io.BytesIO`; note the buffer is seek(0) before return
2. **`TTSResult`** — change `audio: bytes` to `audio: io.BytesIO`
3. **`/process` endpoint** — update the response section: `StreamingResponse` receives the `BytesIO` directly; document that iteration yields bytes chunks and the client reassembles them

## Acceptance criteria

- [x] `_tensor_to_wav_bytes` signature in CONTEXT.md matches the code
- [x] `TTSResult.audio` type documented as `io.BytesIO`
- [x] No stale `bytes` references remain in the relevant sections
- [x] Review: any other docs references to the old return type?

## Blocked by

None — can start immediately (content changes are independent; can be done before or after test fixes)
