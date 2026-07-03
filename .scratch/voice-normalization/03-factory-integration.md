---
title: "Integrate VoiceNormalization into TextNormalizerFactory + wire storage"
labels:
  - ready-for-human
created: 2026-07-03
---

## What to build

Add `storage: SileroTTSConfigStorage` parameter to `TextNormalizerFactory.__init__`. Implement a new code path in `create_text_normalizer` that checks for VoiceNormalization before falling through to the existing system-default builder lookup. Update `main.py` to pass storage to the factory.

## Acceptance criteria

- [x] `TextNormalizerFactory.__init__` accepts `storage: SileroTTSConfigStorage` parameter
- [x] `create_text_normalizer(voice, format)` checks `storage.get_voice_normalization(voice.id, format)` first
- [x] If VoiceNormalization found and `enabled: false` → returns `None` (skip normalization)
- [x] If VoiceNormalization found and `enabled: true` and `type: simple` → returns `PlainTextNormalizer()` or `SsmlNormalizer()`
- [x] If VoiceNormalization found and `enabled: true` and `type: llm` → resolves `Promt` via `storage.get_promt(vn.promt_id)` and returns `OpenAiTextNormalizer`
- [x] If no VoiceNormalization found → falls through to existing system-default logic (unchanged)
- [x] `main.py` passes `storage` to `TextNormalizerFactory` constructor
- [x] Existing tests still pass

## Blocked by

- Slice 1: Promt + VoiceNormalization entities must exist
- Slice 2: Config storage methods must be implemented
