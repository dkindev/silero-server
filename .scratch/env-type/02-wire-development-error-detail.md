---
title: "Wire TTS_ENV_TYPE into GlobalExceptionMiddleware for detailed errors in development"
labels:
  - ready-for-agent
created: 2026-06-07
---

## What to build

Make the `GlobalExceptionMiddleware` in `src/handlers.py` read the `TTS_ENV_TYPE` setting and conditionally include exception details in 500 responses.

- When `TTS_ENV_TYPE=development`: include the exception message in the `"detail"` field of the JSON error response (e.g., `{"detail": "list index out of range", "request_id": "..."}`)
- When `TTS_ENV_TYPE=production` (or default): keep the current generic `{"detail": "Internal Server Error", "request_id": "..."}`

Access settings via the cached `get_settings()` function. No need to thread settings through middleware constructor.

## Acceptance criteria

- [x] Development mode: 500 responses include the exception message in `detail`
- [x] Production mode: 500 responses return generic `"Internal Server Error"`
- [x] Default (`development`): detailed errors shown (matches default)
- [x] Tests cover both modes (e.g., inject a route that raises and assert different response bodies)
- [x] Existing tests pass unchanged

## Blocked by

- `01-add-tts-env-type-to-settings.md`
