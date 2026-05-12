---
title: "Stage 1: GET /api/v1/voices Endpoint"
labels:
  - ready-for-agent
created: 2026-05-12
---

## Parent

docs/stages/1.md

## What to build

Create `src/routers/voices.py` — GET /api/v1/voices endpoint.

- Returns text/plain response, one voice per line: `{voice} {locale} {gender}\n`.
- Example: `silero-v5_5_ru-aidar ru_RU male\nsilero-v5_5_ru-baya ru_RU female\n...`
- Lazy discovery: parse cached models on first call, cache in memory.
- Returns 200 OK even when no voices available.

## Acceptance criteria

- [ ] GET /api/v1/voices returns 200 OK
- [ ] Content-Type: text/plain
- [ ] One voice per line in format: `{voice} {locale} {gender}`
- [ ] Voice names prefixed with silero- (e.g., silero-v5_5_ru-aidar)
- [ ] Deduplication of duplicate voices
- [ ] Lazy discovery (first call parses, subsequent calls use cache)

## Blocked by

- Stage 1: Silero Wrapper Module