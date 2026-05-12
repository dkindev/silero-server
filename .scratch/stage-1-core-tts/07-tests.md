---
title: "Stage 1: Tests for All Endpoints"
labels:
  - ready-for-agent
created: 2026-05-12
---

## Parent

docs/stages/1.md

## What to build

Create test files for all endpoints:

**test_locales.py:**
- Test 200 OK response
- Test text/plain content type
- Test response format (one locale per line)
- Mock Silero model discovery

**test_voices.py:**
- Test 200 OK response
- Test text/plain content type
- Test response format (one voice per line)
- Test deduplication
- Mock Silero model discovery

**test_process.py:**
- Test GET success → 200 + audio/wav
- Test POST success → 200 + audio/wav
- Test missing INPUT_TEXT → 400
- Test text too long → 400
- Test unsupported locale → 400
- Test unsupported voice → 400
- Test invalid INPUT_TYPE → 400
- Test OUTPUT_TYPE=PHONEMES → 406
- Test locale/text mismatch → 400
- Mock Silero synthesis

## Acceptance criteria

- [ ] test_locales.py passes — all locales endpoint cases covered
- [ ] test_voices.py passes — all voices endpoint cases covered
- [ ] test_process.py passes — all process endpoint cases covered
- [ ] Tests mock Silero (no actual model loading)
- [ ] Tests verify external behavior (HTTP status, headers, body type), not implementation details

## Blocked by

- Stage 1: Main.py Integration