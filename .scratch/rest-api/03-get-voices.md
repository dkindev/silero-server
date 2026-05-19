---
title: "GET /voices endpoint"
labels:
  - needs-triage
created: 2026-05-19
---

## What to build

Implement `GET /voices` returning available voices in Mary-TTS format.

- Create `src/routers/voices.py` with GET endpoint
- Return `Content-Type: text/plain`
- Response body: one voice per line in Mary-TTS format (`silero-v5_5_ru-aidar ru_RU male`)

## Acceptance criteria

- [x] GET /voices returns 200
- [x] Content-Type is text/plain
- [x] Body contains voices in Mary-TTS format, one per line

## Blocked by

01-router-infrastructure