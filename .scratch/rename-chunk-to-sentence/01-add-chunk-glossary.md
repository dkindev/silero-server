---
title: "Add 'Chunk' to CONTEXT.md glossary, fix example dialogue"
labels:
  - ready-for-agent
created: 2026-07-13
---

## What to build

Add **Chunk** as a domain term to CONTEXT.md — raw PCM audio bytes produced by the TTS Engine for streaming over the Wyoming protocol. Fix the example dialogue to use **Sentence** where the text-splitting concept was incorrectly called "Chunk", and abstract the Wyoming protocol details.

## Acceptance criteria

- [x] "Chunk" term defined in CONTEXT.md glossary with `_Avoid_` aliases
- [x] Example dialogue uses "Sentence" for text-splitting concept, not "Chunk"
- [x] Example dialogue abstracts Wyoming protocol details instead of enumerating raw protocol events
- [x] TTS Engine → Chunks relationship is added to the Relationships section
- [x] All existing terms and relationships remain intact

## Blocked by

- None - can start immediately
