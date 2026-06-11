---
title: "Rewrite CONTEXT.md as domain glossary"
labels:
  - ready-for-agent
created: 2026-06-11
---

## What to build

Strip CONTEXT.md down to a pure domain glossary. Remove all:

- YAML config snippets and field descriptions
- Environment variable tables
- Endpoint definitions (/process, /locales, /voices, /health)
- HTTP status codes and error response formats
- Text preprocessing chunking strategy
- Cache eviction and concurrency details
- Docker strategy, CORS, graceful shutdown
- File paths and code snippets

Keep only domain-level glossary terms: TTS Engine, Model, Speaker, Sample Rate,
Locale, Voice, Input Type, Output Type, Chunk. Merge the "TTS Engine" and
"SileroTTSEngine" entries into one. The result should be comprehensible to a
domain expert with no code access.

## Acceptance criteria

- [ ] CONTEXT.md contains only glossary entries, no implementation details
- [ ] Each term has a 1–3 sentence definition
- [ ] "TTS Engine" and "SileroTTSEngine" are merged into one concept
- [ ] No YAML snippets, no file paths, no env var names, no endpoint paths
- [ ] README.md is not modified by this issue

## Blocked by

None — can start immediately
