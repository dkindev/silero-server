---
title: "Slice 3: Chunk + finishing polish"
labels:
  - ready-for-agent
created: 2026-06-18
---

## What to build

Add the Chunk term and apply finishing polish across the entire CONTEXT.md. Verify every term has a definition, an `_Avoid_` alias, and participates in at least one relationship. Confirm the Flagged ambiguities section and Example dialogue are complete and coherent.

Add:

- **Chunk**: A segment of text split from the input to stay within model length limits. Multiple chunks are synthesized separately and streamed as a single audio response. *Avoid*: Segment, fragment

Extend **Relationships**:
- The TTS Engine loads a Model, selects a Speaker, splits text into Chunks, and outputs PCM audio

Extend **Example dialogue** with Q&A about chunking behavior.

**Polish pass**:
- Ensure every term has an `_Avoid_` line (some may have been added without it)
- Ensure the Flagged ambiguities section lists both ambiguities:
  - "Mary-TTS compatible REST API" → resolved: this is a Wyoming protocol server
  - "Model" as both config entry and loaded network → resolved: Model is a configuration concept
- Ensure the Example dialogue covers all 7 terms in a natural conversation
- Trim any remaining implementation-level detail (function names, dataclass field names, TTSResult references)

## Acceptance criteria

- [x] Chunk is defined with `_Avoid_` alias
- [x] Relationships include TTS Engine → Chunks → audio output
- [x] Example dialogue covers chunking behavior
- [x] Flagged ambiguities lists both resolved ambiguities
- [x] Every term has an `_Avoid_` alias
- [x] No implementation-level detail leaks into definitions

## Blocked by

- Slice 2: Integration layer — Locale, Voice, Wyoming
