---
title: "Integration tests for API"
labels:
  - needs-triage
created: 2026-05-19
---

## What to build

Add integration tests that test the full HTTP flow.

Tests are already implemented in `tests/test_routers.py`:
- Test /locales returns expected format
- Test /voices returns expected format
- Test /process with valid params returns WAV
- Test /process with invalid locale returns 400
- Test /process with invalid voice returns 400
- Test GET and POST variants

## Acceptance criteria

- [x] Tests pass
- [x] Cover happy path and error cases

## Blocked by

05-post-process