---
title: "POST /process endpoint"
labels:
  - needs-triage
created: 2026-05-19
---

## What to build

Implement `POST /process` for text-to-speech synthesis via form data.

- Add POST endpoint in `src/routers/process.py`
- Accept form data with same params as GET: INPUT_TEXT, INPUT_TYPE, OUTPUT_TYPE, LOCALE, VOICE, AUDIO
- Reuse validation logic from GET
- Return same WAV response format

## Acceptance criteria

- [x] POST /process with form data returns WAV
- [x] Same validation as GET
- [x] Same response format as GET

## Blocked by

04-get-process