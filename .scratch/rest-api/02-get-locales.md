---
title: "GET /locales endpoint"
labels:
  - needs-triage
created: 2026-05-19
---

## What to build

Implement `GET /locales` returning supported locales in plain text format.

- Create `src/routers/locales.py` with GET endpoint
- Return `Content-Type: text/plain`
- Response body: one locale per line (e.g., `ru_RU\nde_DE`)

## Acceptance criteria

- [x] GET /locales returns 200
- [x] Content-Type is text/plain
- [x] Body contains locales, one per line

## Blocked by

01-router-infrastructure