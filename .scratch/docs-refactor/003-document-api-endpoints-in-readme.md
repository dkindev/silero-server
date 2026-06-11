---
title: "Document API endpoints in README"
labels:
  - ready-for-agent
created: 2026-06-11
---

## What to build

Extend the "API Endpoints" section of README.md (currently only has `/health`)
to document all endpoints:

- **`/process`** — parameters (INPUT_TEXT, LOCALE, VOICE, INPUT_TYPE,
OUTPUT_TYPE, AUDIO), validation rules, response format (WAV audio)
- **`/locales`** — returns plain-text list of supported Mary-TTS locales
- **`/voices`** — returns plain-text list of voices in Mary-TTS format
- **`/health`** — already present, ensure format is consistent

This content is currently in CONTEXT.md and should be in README where API
consumers will find it.

## Acceptance criteria

- [ ] README.md lists all four endpoints with parameters, types, and
descriptions
- [ ] Parameter tables include required/optional status and defaults
- [ ] Response format is described for each endpoint
- [ ] Validation rules (400/406/500) are documented
- [ ] CONTEXT.md is not modified by this issue

## Blocked by

None — can start immediately
