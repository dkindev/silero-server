---
title: "Update .env.example with missing sections"
labels:
  - ready-for-agent
created: 2026-07-06
---

## What to build

Add the missing normalization and openai environment variable sections to `.env.example`. Currently it only covers infrastructure, torch, and TTS configuration.

Add sections:
- **Normalization**: `TTS_NORMALIZATION__TIMEOUT`, `TTS_NORMALIZATION__MAX_CONCURRENT_CHUNKS_PER_REQUEST`, `TTS_NORMALIZATION__TEXT_ENABLED`, `TTS_NORMALIZATION__TEXT_TYPE`, `TTS_NORMALIZATION__SSML_ENABLED`, `TTS_NORMALIZATION__SSML_TYPE`
- **OpenAI**: `TTS_OPENAI__BASE_URL`, `TTS_OPENAI__API_KEY`

Default values must match config.yml defaults:
- `TTS_NORMALIZATION__TIMEOUT=5`
- `TTS_NORMALIZATION__MAX_CONCURRENT_CHUNKS_PER_REQUEST=2`
- `TTS_NORMALIZATION__TEXT_ENABLED=true`
- `TTS_NORMALIZATION__TEXT_TYPE=simple`
- `TTS_NORMALIZATION__SSML_ENABLED=false`
- `TTS_NORMALIZATION__SSML_TYPE=simple`
- `TTS_OPENAI__BASE_URL=`
- `TTS_OPENAI__API_KEY=`

## Acceptance criteria

- [x] Normalization section added with all 6 env vars and correct defaults
- [x] OpenAI section added with both env vars
- [x] Each variable has a comment explaining its purpose
- [x] Default values match config.yml

## Blocked by

None - can start immediately
