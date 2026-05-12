---
title: "Stage 1: GET+POST /api/v1/process Endpoint"
labels:
  - ready-for-agent
created: 2026-05-12
---

## Parent

docs/stages/1.md

## What to build

Create `src/routers/process.py` — TTS synthesis endpoint supporting GET and POST.

**GET params / POST form fields:**
- INPUT_TEXT (required)
- LOCALE (required, e.g., ru_RU)
- VOICE (required, e.g., silero-v5_5_ru-aidar)
- INPUT_TYPE (optional, default TEXT; SSML strips tags; RAWMARYXML rejected 400)
- OUTPUT_TYPE (optional, default AUDIO; PHONEMES/TOKENS rejected 406)

**Validation chain (400 on any failure):**
1. INPUT_TEXT present and non-empty
2. Length ≤ TTS_MAX_TEXT_LENGTH
3. LOCALE supported (model cached)
4. VOICE valid for locale
5. Text language matches LOCALE (Cyrillic check for Russian, Latin check for English/German)
6. INPUT_TYPE ∈ {TEXT, SSML}. SSML → strip tags before synthesis
7. OUTPUT_TYPE = AUDIO. PHONEMES/TOKENS → 406

**Concurrency:**
- Per-locale asyncio.Semaphore(2) — max 2 concurrent requests per locale
- Different locales run in parallel

**Success response:**
- Body: raw WAV bytes
- Content-Type: audio/wav
- Content-Disposition: inline
- X-Generated-By: Silero-TTS-Server

## Acceptance criteria

- [ ] GET /api/v1/process?INPUT_TEXT=...&LOCALE=...&VOICE=... returns 200 + audio/wav
- [ ] POST /api/v1/process with form body returns 200 + audio/wav
- [ ] Missing INPUT_TEXT → 400
- [ ] Text exceeds max length → 400
- [ ] Unsupported locale → 400
- [ ] Invalid voice for locale → 400
- [ ] Text language doesn't match locale → 400
- [ ] INPUT_TYPE=RAWMARYXML → 400
- [ ] OUTPUT_TYPE=PHONEMES → 406
- [ ] OUTPUT_TYPE=TOKENS → 406
- [ ] SSML input → tags stripped before synthesis
- [ ] Per-locale concurrency limited to 2
- [ ] Correct response headers (Content-Type, Content-Disposition, X-Generated-By)

## Blocked by

- Stage 1: Silero Wrapper Module